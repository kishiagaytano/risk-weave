"""Model-family blend search on the clean features.

Trains extra model families (histogram gradient boosting, extra trees, random forest, a small MLP) with the same
5-fold split as the existing ensemble, searches equal-weight and non-negative-stacking blends, and judges them by
out-of-fold AUC and by realised profit under three loss formulas. A blend is accepted only if it beats the current
ensemble by a margin in at least n_folds - 1 folds (see ``accept``). Nothing here looks at public scores.

Loss formulas: loss = R x max(loan - k x monthly payment, 0); gain = total interest. Only libraries available inside
VFL are used.
"""
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.optimize import nnls
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline

from . import config, cv, data, final, models, policy, submission
from .features import make_preprocessor, to_numpy_safe

FORMULAS = {"main": (0.7, 18), "alt": (0.8, 23), "orig": (0.5, 0)}
BASE_NAMES = ("lr", "xgb_d2", "xgb_d3")
MIN_AUC_GAIN = 0.001
MIN_PROFIT_GAIN = 0.2          # $M (realised, on the 100,000 labelled loans)


# ---- model families --------------------------------------------------------------------------------------------
def hgb(X, depth=3, fast=False, **params):
    base = dict(max_iter=30 if fast else 300, learning_rate=0.05, max_depth=depth, min_samples_leaf=50,
                l2_regularization=5.0, early_stopping=False, random_state=config.SEED)
    base.update(params)
    return Pipeline([("prep", make_preprocessor(X, scale=False)), ("model", HistGradientBoostingClassifier(**base))])


def mlp(X, fast=False, **params):
    base = dict(hidden_layer_sizes=(16,) if fast else (32, 16), alpha=1e-2, learning_rate_init=1e-3, batch_size=256,
                early_stopping=True, n_iter_no_change=8, max_iter=15 if fast else 60, random_state=config.SEED)
    base.update(params)
    return Pipeline([("prep", make_preprocessor(X, scale=True)), ("model", MLPClassifier(**base))])


FACTORIES = {
    "lr": lambda X, fast=False: models.logreg(X, C=0.1),
    "xgb_d2": lambda X, fast=False: models.xgboost(X, **{**final.XGB_D2, **({"n_estimators": 30} if fast else {})}),
    "xgb_d3": lambda X, fast=False: models.xgboost(X, **{**final.XGB_D3, **({"n_estimators": 30} if fast else {})}),
    "hgb_d3": lambda X, fast=False: hgb(X, 3, fast),
    "hgb_d2": lambda X, fast=False: hgb(X, 2, fast, max_iter=30 if fast else 500),
    "et": lambda X, fast=False: models.forest(X, "et", n_estimators=20 if fast else 300, min_samples_leaf=30),
    "rf": lambda X, fast=False: models.forest(X, "rf", n_estimators=20 if fast else 300, min_samples_leaf=30),
    "mlp": lambda X, fast=False: mlp(X, fast),
}
NEW_FAMILIES = ("hgb_d3", "hgb_d2", "et", "rf", "mlp")


# ---- economics -------------------------------------------------------------------------------------------------
def econ(df):
    """Arrays needed to value decisions: loan amount, monthly payment, gain if repaid (total interest)."""
    return {"amt": df["LOAN_AMOUNT"].to_numpy(float), "pay": df["MONTHLY_PAYMENT"].to_numpy(float),
            "gain": policy.loan_gain(df, "interest_total")}


def loss_vector(e, R, k):
    return R * np.maximum(e["amt"] - k * e["pay"], 0.0)


def rule(e, p, R, k):
    """Approve when (1 - p) x gain > p x loss."""
    return ((1 - p) * e["gain"] - p * loss_vector(e, R, k)) > 0


def profit(e, y, approved, R, k, idx=None):
    """Realised profit in $M of the approved loans (optionally on a subset of rows)."""
    v = np.where(np.asarray(y) == 1, -loss_vector(e, R, k), e["gain"])
    a = np.asarray(approved, bool)
    if idx is not None:
        v, a = v[idx], a[idx]
    return float(v[a].sum()) / 1e6


# ---- out-of-fold predictions ----------------------------------------------------------------------------------
def folds_for(y, n_folds=config.N_FOLDS):
    return list(StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=config.SEED).split(np.zeros(len(y)), y))


def family_oof(X, y, name, fast=False, n_folds=config.N_FOLDS, out_dir=None):
    """OOF probabilities for one family; resumes from out_dir/<name>_clean.npy (row 0 = y, row 1 = prediction)."""
    path = Path(out_dir) / f"{name}_clean.npy" if out_dir else None
    if path is not None and path.exists():
        a = np.load(path)
        if a.shape == (2, len(y)):
            return a[1], None
    oof, aucs, _ = cv.oof_predict(FACTORIES[name](X, fast), X, y, n_folds=n_folds)
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(path, np.array([np.asarray(y, float), oof]))
    return oof, aucs


# ---- evaluation and acceptance --------------------------------------------------------------------------------
def evaluate(p, y, e, folds):
    y = np.asarray(y)
    out = {"auc": float(roc_auc_score(y, p)), "fold_auc": [float(roc_auc_score(y[v], p[v])) for _, v in folds]}
    for name, (R, k) in FORMULAS.items():
        ap = rule(e, p, R, k)
        out[f"profit_{name}"] = profit(e, y, ap, R, k)
        out[f"fold_profit_{name}"] = [profit(e, y, ap, R, k, idx=v) for _, v in folds]
        out[f"approval_{name}"] = float(ap.mean())
    return out


def accept(base, cand, min_auc=MIN_AUC_GAIN, min_profit=MIN_PROFIT_GAIN):
    """Candidate must beat the base by a margin overall and in at least n_folds - 1 folds, on AUC or on profit."""
    n = len(base["fold_auc"])
    need = n - 1
    d_auc = cand["auc"] - base["auc"]
    wins_auc = sum(c > b for c, b in zip(cand["fold_auc"], base["fold_auc"]))
    d_pro = cand["profit_main"] - base["profit_main"]
    wins_pro = sum(c > b for c, b in zip(cand["fold_profit_main"], base["fold_profit_main"]))
    ok_auc, ok_pro = d_auc > min_auc and wins_auc >= need, d_pro > min_profit and wins_pro >= need
    return {"accepted": bool(ok_auc or ok_pro), "by_auc": bool(ok_auc), "by_profit": bool(ok_pro),
            "d_auc": float(d_auc), "d_profit_main": float(d_pro), "fold_wins_auc": int(wins_auc),
            "fold_wins_profit": int(wins_pro)}


# ---- blends -----------------------------------------------------------------------------------------------------
def nnls_weights(P, y):
    """Non-negative weights summing to 1 for probability-space stacking."""
    w, _ = nnls(np.asarray(P, float).T, np.asarray(y, float))
    s = w.sum()
    return w / s if s > 0 else np.full(len(w), 1.0 / len(w))


def stacked_oof(P, y, folds):
    """Nested stacking: weights for each held-out fold come from the other folds only."""
    P = np.asarray(P, float)
    out = np.zeros(P.shape[1])
    for t, v in folds:
        out[v] = nnls_weights(P[:, t], np.asarray(y)[t]) @ P[:, v]
    return out


def search(P, y, e, folds, max_size=4):
    """Evaluate the base ensemble, every equal-weight subset (size 1..max_size) and the nested stack."""
    names = list(P)
    results = {}
    for r in range(1, min(max_size, len(names)) + 1):
        for sub in itertools.combinations(names, r):
            results["+".join(sub)] = evaluate(np.mean([P[n] for n in sub], axis=0), y, e, folds)
    M = np.array([P[n] for n in names])
    results["stack"] = evaluate(stacked_oof(M, y, folds), y, e, folds)
    results["stack"]["weights"] = dict(zip(names, np.round(nnls_weights(M, y), 4).tolist()))
    return results


def pick(results, base_key, top=5):
    """Top candidates by AUC and by main-formula profit, each with its acceptance verdict against the base."""
    base = results[base_key]
    rows = []
    for key, r in results.items():
        if key == base_key:
            continue
        rows.append({"blend": key, "auc": r["auc"], "profit_main": r["profit_main"], **accept(base, r)})
    by_auc = sorted(rows, key=lambda t: -t["auc"])[:top]
    by_profit = sorted(rows, key=lambda t: -t["profit_main"])[:top]
    return by_auc, by_profit


# ---- scoring-side candidate --------------------------------------------------------------------------------------
def blend_weights(P, y, key):
    names = list(P)
    if key == "stack":
        return dict(zip(names, nnls_weights(np.array([P[n] for n in names]), y).tolist()))
    sub = key.split("+")
    return {n: 1.0 / len(sub) for n in sub}


def fit_blend_scores(train, score, weights, feature_set="clean", fast=False):
    """Fit every member with non-zero weight on all labelled rows and return the weighted mean PD on the scoring rows."""
    X, y, _ = data.split_xy(train)
    cols = config.feature_columns(train.columns, feature_set)
    Xt, Xs = to_numpy_safe(X[cols]), to_numpy_safe(score[cols])
    total, p = 0.0, np.zeros(len(score))
    for name, w in weights.items():
        if w <= 0:
            continue
        p += w * FACTORIES[name](Xt, fast).fit(Xt, y).predict_proba(Xs)[:, 1]
        total += w
    return p / total


def build_candidate(score, p, formula="main"):
    """Validated LOAN_ID,APPROVED frame from the rule with the chosen loss formula."""
    R, k = FORMULAS[formula]
    sub = submission.build(score[config.ID_COL], rule(econ(score), p, R, k).astype(int))
    submission.validate(sub, score[config.ID_COL])
    return sub


# ---- experiment driver ---------------------------------------------------------------------------------------------
def run_experiment(train, score=None, out_dir=None, families=NEW_FAMILIES, base_oof=None, fast=False,
                   n_folds=config.N_FOLDS):
    """Train the families, search blends, apply the acceptance rule and (if one passes and ``score`` is given) build
    one candidate. ``base_oof`` maps lr / xgb_d2 / xgb_d3 to saved OOF arrays (otherwise they are recomputed)."""
    X, y, _ = data.split_xy(train)
    y = np.asarray(y).astype(int)
    cols = config.feature_columns(train.columns, "clean")
    X = to_numpy_safe(X[cols])
    e, folds = econ(train), folds_for(y, n_folds)
    P, aucs = {}, {}
    for name in BASE_NAMES:
        if base_oof and name in base_oof:
            P[name] = np.asarray(base_oof[name], float)
        else:
            P[name], aucs[name] = family_oof(X, y, name, fast, n_folds, out_dir)
    for name in families:
        P[name], aucs[name] = family_oof(X, y, name, fast, n_folds, out_dir)
    base_key = "+".join(BASE_NAMES)
    results = search(P, y, e, folds)
    singles = {n: evaluate(P[n], y, e, folds) for n in P}
    by_auc, by_profit = pick(results, base_key)
    winner = next((r for r in by_auc + by_profit if r["accepted"]), None)
    out = {"base": results[base_key], "singles": {n: {"auc": s["auc"], "profit_main": s["profit_main"]}
                                                  for n, s in singles.items()},
           "top_by_auc": by_auc, "top_by_profit": by_profit, "winner": winner, "stack_weights": results["stack"]["weights"],
           "candidate": None}
    if winner is not None and score is not None:
        weights = blend_weights(P, y, winner["blend"])
        p = fit_blend_scores(train, score, weights, fast=fast)
        sub = build_candidate(score, p, "main")
        out["candidate"] = {"blend": winner["blend"], "weights": weights, "approval": float(sub["APPROVED"].mean()),
                            "frame": sub}
    if out_dir:
        slim = {k: v for k, v in out.items() if k != "candidate"}
        slim["candidate"] = None if out["candidate"] is None else {k: v for k, v in out["candidate"].items() if k != "frame"}
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        (Path(out_dir) / "blend_summary.json").write_text(json.dumps(slim, indent=1, default=float))
    return out

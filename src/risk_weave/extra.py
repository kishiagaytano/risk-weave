"""Extra experiments: stake-weighted and profit-aware models, engineered features,
collateral-aware loss and stacking. Model inputs stay within the `clean` feature set
(no sensitive, proxy, timing-uncertain or pricing fields); engineered columns are
derived only from clean columns. LOAN_AMOUNT / MONTHLY_PAYMENT / LOAN_TERM are used in
the decision rule and (as ordinary clean fields) as model inputs."""
import numpy as np
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from . import config, policy
from .features import to_numpy_safe

GAIN = "interest_total"


def _col(df, name):
    return df[name].to_numpy(float) if name in df.columns else None


def add_features(df):
    """Append ratio/interaction features built from clean fields only."""
    out = df.copy()
    inc, rep = _col(df, "HOUSEHOLD_INCOME"), _col(df, "REPORTED_INCOME")
    amt, pay = _col(df, "LOAN_AMOUNT"), _col(df, "MONTHLY_PAYMENT")
    exp = _col(df, "MONTHLY_EXPENSES")
    sav, chk = _col(df, "SAVINGS_BALANCE"), _col(df, "CHECKING_BALANCE")
    dti, ltv, util = _col(df, "DEBT_TO_INCOME"), _col(df, "LOAN_TO_VALUE"), _col(df, "REVOLVING_UTILIZATION")
    with np.errstate(divide="ignore", invalid="ignore"):
        if inc is not None and rep is not None:
            out["F_INCOME_GAP"] = (rep - inc) / np.maximum(inc, 1.0)
        if inc is not None and amt is not None:
            out["F_LOAN_TO_INCOME"] = amt / np.maximum(inc, 1.0)
        if inc is not None and pay is not None and exp is not None:
            out["F_PAY_AFTER_EXPENSES"] = pay / np.maximum(inc / 12.0 - exp, 1.0)
        if pay is not None and (sav is not None or chk is not None):
            buf = np.nan_to_num(sav if sav is not None else 0.0) + np.nan_to_num(chk if chk is not None else 0.0)
            out["F_BUFFER_MONTHS"] = buf / np.maximum(pay, 1.0)
        if util is not None and dti is not None:
            out["F_UTIL_X_DTI"] = util * dti
        if dti is not None and ltv is not None:
            out["F_DTI_X_LTV"] = dti * ltv
    d = [_col(df, c) for c in ("DELINQ_30", "DELINQ_60", "DELINQ_90", "MISSED_PAYMENTS_12M")]
    if all(x is not None for x in d):
        out["F_DELINQ_SCORE"] = d[0] + 2 * d[1] + 3 * d[2] + d[3]
    return out


def stake_weights(df, y, lgd=0.5):
    """Dollar stake of each row: interest if repaid, lgd x amount if defaulted (mean 1)."""
    gain = policy.loan_gain(df, GAIN)
    loss = lgd * df["LOAN_AMOUNT"].to_numpy(float)
    w = np.where(np.asarray(y) == 1, loss, gain)
    return w / w.mean()


def profit_target(df, y, lgd=0.5):
    gain = policy.loan_gain(df, GAIN)
    loss = lgd * df["LOAN_AMOUNT"].to_numpy(float)
    return np.where(np.asarray(y) == 1, -loss, gain)


def collateral_loss_fraction(df, mean_loss=0.5):
    """Per-loan loss fraction = max(1 - r * value / amount, 0.05), value = amount / LTV.

    r (share of the vehicle value recovered) is solved so the average fraction equals
    `mean_loss`, keeping the rule consistent with the flat-0.5 fit. Higher LTV (thin
    equity) therefore means a bigger loss. The shape is an assumption.
    """
    ltv = np.clip(df["LOAN_TO_VALUE"].to_numpy(float), 0.2, 1.5)
    ltv = np.where(np.isnan(ltv), np.nanmedian(ltv), ltv)

    def mean_for(r):
        return np.mean(np.clip(1.0 - r / ltv, 0.05, 1.0))

    lo, hi = 0.0, 1.5
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if mean_for(mid) > mean_loss else (lo, mid)
    return np.clip(1.0 - ((lo + hi) / 2) / ltv, 0.05, 1.0)


def rule_decisions(df, p, loss_fraction):
    """Approve when (1-p)*gain > p*loss; loss_fraction may be a scalar or per-loan."""
    gain = policy.loan_gain(df, GAIN)
    loss = np.asarray(loss_fraction) * df["LOAN_AMOUNT"].to_numpy(float)
    return ((1 - p) * gain - p * loss) > 0


def uncertainty_adjusted_pd(member_pds, k=1.0):
    """Ensemble PD plus k standard deviations of the member PDs, clipped to [0, 1].

    Members that disagree make the estimate less certain, so the adjusted PD is larger
    exactly where the models disagree; with k = 0 it is the plain equal-weight mean."""
    m = np.asarray(member_pds, float)
    return np.clip(m.mean(axis=0) + k * m.std(axis=0), 0.0, 1.0)


def profit_at(df, y, approved, lgd=0.5):
    return policy.realised_profit(df, y, approved, GAIN, lgd)


def oof_weighted(estimator, X, y, weights=None, n_folds=config.N_FOLDS, seed=config.SEED):
    """OOF probabilities from a pipeline fitted with optional sample weights."""
    X = to_numpy_safe(X)
    y = np.asarray(y)
    oof = np.zeros(len(y))
    for tr, va in StratifiedKFold(n_folds, shuffle=True, random_state=seed).split(X, y):
        m = clone(estimator)
        kw = {} if weights is None else {"model__sample_weight": weights[tr]}
        m.fit(X.iloc[tr], y[tr], **kw)
        oof[va] = m.predict_proba(X.iloc[va])[:, 1]
    return oof


def oof_profit_regressor(regressor, X, target, y, n_folds=config.N_FOLDS, seed=config.SEED):
    """OOF predictions of per-loan profit from a regressor pipeline (stratified on y)."""
    X = to_numpy_safe(X)
    oof = np.zeros(len(target))
    for tr, va in StratifiedKFold(n_folds, shuffle=True, random_state=seed).split(X, np.asarray(y)):
        m = clone(regressor).fit(X.iloc[tr], target[tr])
        oof[va] = m.predict(X.iloc[va])
    return oof


def stack_oof(oofs, y, n_folds=config.N_FOLDS, seed=config.SEED + 7):
    """Cross-fitted logistic meta-learner on the logits of base OOF predictions."""
    clipped = [np.clip(o, 1e-6, 1 - 1e-6) for o in oofs]
    Z = np.column_stack([np.log(c / (1 - c)) for c in clipped])
    y = np.asarray(y)
    out = np.zeros(len(y))
    for tr, va in StratifiedKFold(n_folds, shuffle=True, random_state=seed).split(Z, y):
        out[va] = LogisticRegression(C=10.0, max_iter=1000).fit(Z[tr], y[tr]).predict_proba(Z[va])[:, 1]
    return out


def best_cutoff_profit(df, y, p, lgd=0.5, grid=None):
    grid = np.arange(0.1, 0.5, 0.01) if grid is None else grid
    vals = [profit_at(df, y, p < t, lgd) for t in grid]
    i = int(np.argmax(vals))
    return float(vals[i]) / 1e6, float(grid[i])


def summary(df, y, p=None, decisions=None):
    """Profit in $M under loss 0.4/0.5/0.6 for a probability (best cutoff and rule) or decisions."""
    res = {}
    for loss in (0.4, 0.5, 0.6):
        if decisions is not None:
            res[f"dec_{loss}"] = round(profit_at(df, y, decisions, loss) / 1e6, 1)
        else:
            res[f"cut_{loss}"] = round(best_cutoff_profit(df, y, p, loss)[0], 1)
            res[f"rule_{loss}"] = round(profit_at(df, y, rule_decisions(df, p, loss), loss) / 1e6, 1)
    if p is not None:
        res["auc"] = round(float(roc_auc_score(y, p)), 4)
    return res

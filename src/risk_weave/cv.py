"""Cross-validation producing out-of-fold probabilities."""
import time

import numpy as np
from sklearn.base import clone
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from .config import N_FOLDS, SEED
from .features import to_numpy_safe
from .metrics import summarise


def oof_predict(estimator, X, y, n_folds=N_FOLDS, seed=SEED):
    """Return (oof probabilities, per-fold AUCs, seconds)."""
    X = to_numpy_safe(X)
    y = np.asarray(y)
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    oof = np.zeros(len(y))
    aucs = []
    t0 = time.time()
    for tr, va in skf.split(X, y):
        m = clone(estimator).fit(X.iloc[tr], y[tr])
        oof[va] = m.predict_proba(X.iloc[va])[:, 1]
        aucs.append(float(roc_auc_score(y[va], oof[va])))
    return oof, aucs, time.time() - t0


def calibrate_oof(oof, y, method="isotonic", n_folds=5, seed=SEED):
    """Cross-fitted calibration of OOF scores (calibrator never sees its own rows)."""
    y = np.asarray(y)
    out = np.zeros_like(oof, dtype=float)
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed + 1)
    for tr, va in skf.split(oof.reshape(-1, 1), y):
        if method == "isotonic":
            cal = IsotonicRegression(out_of_bounds="clip", y_min=1e-6, y_max=1 - 1e-6).fit(oof[tr], y[tr])
            out[va] = cal.predict(oof[va])
        else:
            z = np.log(np.clip(oof, 1e-6, 1 - 1e-6) / (1 - np.clip(oof, 1e-6, 1 - 1e-6)))
            cal = LogisticRegression(C=1e6).fit(z[tr].reshape(-1, 1), y[tr])
            out[va] = cal.predict_proba(z[va].reshape(-1, 1))[:, 1]
    return out


def evaluate(oof, y, aucs=None):
    res = summarise(y, oof)
    if aucs:
        res["fold_auc_mean"] = float(np.mean(aucs))
        res["fold_auc_std"] = float(np.std(aucs))
    return res

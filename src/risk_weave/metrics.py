"""Ranking, calibration and group metrics for out-of-fold predictions."""
import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score


def ece(y, p, bins=10):
    """Expected calibration error over equal-frequency bins."""
    order = np.argsort(p)
    err, n = 0.0, len(p)
    for idx in np.array_split(order, bins):
        err += len(idx) / n * abs(p[idx].mean() - y[idx].mean())
    return float(err)


def ks(y, p):
    order = np.argsort(-p)
    y = np.asarray(y)[order]
    tpr = np.cumsum(y) / y.sum()
    fpr = np.cumsum(1 - y) / (len(y) - y.sum())
    return float(np.max(np.abs(tpr - fpr)))


def summarise(y, p):
    y = np.asarray(y)
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return {
        "auc": float(roc_auc_score(y, p)),
        "pr_auc": float(average_precision_score(y, p)),
        "logloss": float(log_loss(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "ece": ece(y, p),
        "ks": ks(y, p),
    }


def group_table(groups, y, approved):
    """Approval rate and default rate among approved, per group level."""
    out = {}
    y = np.asarray(y)
    approved = np.asarray(approved).astype(bool)
    for level in sorted(set(groups)):
        m = np.asarray(groups) == level
        a = m & approved
        out[str(level)] = {
            "n": int(m.sum()),
            "approval_rate": float(approved[m].mean()),
            "default_rate_approved": float(y[a].mean()) if a.any() else None,
            "default_rate_all": float(y[m].mean()),
        }
    return out

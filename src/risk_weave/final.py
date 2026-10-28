"""Final ensemble: fit on all labelled rows, score the scoring table, build the
candidate submission. The member list mirrors the cross-validated ensemble in
docs/experiment-log.md (logistic regression + two shallow XGBoost models)."""
import numpy as np

from . import config, data, models, submission
from .features import to_numpy_safe

XGB_D2 = dict(max_depth=2, n_estimators=800, learning_rate=0.05)
XGB_D3 = dict(max_depth=3, n_estimators=500, learning_rate=0.04, min_child_weight=20, reg_lambda=10)
MEMBERS = [("logreg", dict(C=0.1)), ("xgboost", XGB_D2), ("xgboost", XGB_D3)]


def fit_predict(train, score, feature_set="no_rate", members=MEMBERS):
    """Return (mean PD over members, per-member PD list) for the scoring rows."""
    X, y, _ = data.split_xy(train)
    cols = config.feature_columns(train.columns, feature_set)
    missing = [c for c in cols if c not in score.columns]
    if missing:
        raise ValueError(f"scoring table lacks model columns: {missing}")
    Xs = to_numpy_safe(score[cols])
    Xt = to_numpy_safe(X[cols])
    preds = []
    for name, params in members:
        factory = models.logreg if name == "logreg" else models.xgboost
        est = factory(Xt, **params).fit(Xt, y)
        preds.append(est.predict_proba(Xs)[:, 1])
    return np.mean(preds, axis=0), preds


def candidate(score, pd_scores, threshold):
    """Approve when predicted PD is below the threshold; validate the format."""
    approved = (np.asarray(pd_scores) < threshold).astype(int)
    sub = submission.build(score[config.ID_COL], approved)
    submission.validate(sub, score[config.ID_COL])
    return sub

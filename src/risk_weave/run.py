"""Experiment runner usable locally and inside SAS Viya for Learners."""
import numpy as np

from . import config, cv, data, metrics, models, policy
from .experiment_log import log_experiment

EXPERIMENTS = {
    "lr_primary": dict(model="logreg", feature_set="primary", params=dict(C=0.1)),
    "lr_no_rate": dict(model="logreg", feature_set="no_rate", params=dict(C=0.1)),
    "xgb_primary": dict(model="xgboost", feature_set="primary", params={}),
    "xgb_no_rate": dict(model="xgboost", feature_set="no_rate", params={}),
    "xgb_no_proxy": dict(model="xgboost", feature_set="no_proxy", params={}),
    "xgb_no_timing": dict(model="xgboost", feature_set="no_timing", params={}),
    "xgb_with_sensitive": dict(model="xgboost", feature_set="with_sensitive", params={}),
}
FACTORIES = {"logreg": models.logreg, "xgboost": models.xgboost, "forest": models.forest}


def run_experiment(train, name, spec=None, env="local", n_folds=config.N_FOLDS, log_path=None):
    """Cross-validate one configuration, calibrate, choose a robust threshold, log."""
    spec = spec or EXPERIMENTS[name]
    X, y, _ = data.split_xy(train)
    cols = config.feature_columns(train.columns, spec["feature_set"])
    Xf = X[cols]
    est = FACTORIES[spec["model"]](Xf, **spec["params"])
    oof, aucs, secs = cv.oof_predict(est, Xf, y, n_folds=n_folds)
    cal = cv.calibrate_oof(oof, y, "isotonic")
    raw_metrics = cv.evaluate(oof, y, aucs)
    cal_metrics = cv.evaluate(cal, y)
    pol = policy.robust_threshold(train, y.to_numpy(), cal)
    approved = policy.decisions_from_threshold(cal, pol["threshold"])
    fairness = {
        g: metrics.group_table(train[g].to_numpy(), y.to_numpy(), approved)
        for g in config.FAIRNESS_GROUPS if g in train.columns
    }
    rec = dict(
        name=name, env=env, model=spec["model"], params=spec["params"],
        feature_set=spec["feature_set"], n_features=len(cols), seed=config.SEED,
        n_folds=n_folds, n_rows=int(len(train)), seconds=round(secs, 1),
        raw=raw_metrics, calibrated=cal_metrics,
        threshold=pol["threshold"], approval_rate=pol["approval_rate"],
        mean_efficiency=pol["mean_efficiency"], worst_efficiency=pol["worst_efficiency"],
        scenarios=pol["per_scenario"], fairness=fairness,
    )
    log_experiment(rec, **({"path": log_path} if log_path else {}))
    return rec, oof, cal

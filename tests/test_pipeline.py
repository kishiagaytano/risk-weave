import numpy as np
import pandas as pd
import pytest

from risk_weave import config, cv, data, models, policy, submission
from risk_weave.features import to_numpy_safe


def test_feature_sets_exclude_sensitive(synthetic):
    cols = list(synthetic.columns)
    primary = config.feature_columns(cols)
    assert not set(config.SENSITIVE_EXCLUDED) & set(primary)
    assert "LOAN_ID" not in primary and "DEFAULT" not in primary
    assert "INTEREST_RATE" not in config.feature_columns(cols, "no_rate")
    assert set(config.SENSITIVE_EXCLUDED) <= set(config.feature_columns(cols, "with_sensitive"))
    with pytest.raises(ValueError):
        config.feature_columns(cols, "bogus")


def test_audit_and_split(synthetic):
    a = data.audit(synthetic)
    assert a["id_unique"] and a["n_rows"] == len(synthetic)
    X, y, ids = data.split_xy(synthetic)
    assert "DEFAULT" not in X and "LOAN_ID" not in X and len(y) == len(ids)


@pytest.mark.parametrize("factory", [models.logreg, models.xgboost])
def test_oof_has_signal(synthetic, factory):
    X, y, _ = data.split_xy(synthetic)
    X = X[config.feature_columns(synthetic.columns)]
    kwargs = {"n_estimators": 60} if factory is models.xgboost else {}
    oof, aucs, _ = cv.oof_predict(factory(X, **kwargs), X, y, n_folds=3)
    assert oof.shape == y.shape and ((oof >= 0) & (oof <= 1)).all()
    assert np.mean(aucs) > 0.65


def test_calibration_keeps_range(synthetic):
    rng = np.random.default_rng(0)
    p = rng.uniform(size=1000)
    y = (rng.uniform(size=1000) < p).astype(int)
    for method in ("isotonic", "platt"):
        c = cv.calibrate_oof(p, y, method)
        assert ((c >= 0) & (c <= 1)).all()


def test_policy_threshold_and_decisions(synthetic):
    y = synthetic["DEFAULT"].to_numpy()
    p = np.clip(0.1 + 0.5 * (y - 0.1) + np.random.default_rng(1).normal(0, 0.1, len(y)), 0.01, 0.99)
    res = policy.robust_threshold(synthetic, y, p)
    assert 0 < res["threshold"] < 1 and 0 <= res["approval_rate"] <= 1
    d = policy.decisions_from_threshold(p, res["threshold"])
    assert set(np.unique(d)) <= {0, 1}
    rule = policy.expected_profit_rule(synthetic, p, "interest_total", 0.5)
    assert rule.dtype == bool and len(rule) == len(p)


def test_submission_validation():
    ids = [10, 20, 30]
    sub = submission.build(ids, [1, 0, 1])
    assert submission.validate(sub, ids)
    with pytest.raises(ValueError):
        submission.validate(sub.iloc[:2], ids)
    with pytest.raises(ValueError):
        submission.validate(pd.concat([sub, sub.iloc[:1]]), ids)
    bad = sub.copy(); bad["APPROVED"] = [1, 2, 0]
    with pytest.raises(ValueError):
        submission.validate(bad, ids)


def test_sample_files_schema_if_present():
    from pathlib import Path
    tr, sc = Path("ilink_creditrisk_training_sample.csv"), Path("ilink_creditrisk_scoring_sample.csv")
    if not (tr.exists() and sc.exists()):
        pytest.skip("local sample files not present")
    a = data.audit(data.load_csv(tr), data.load_csv(sc))
    assert a["schema_diff"] == ["DEFAULT"] and a["id_overlap"] == 0

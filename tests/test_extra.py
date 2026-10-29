import numpy as np
import pytest
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from risk_weave import config, data, extra, models
from risk_weave.features import make_preprocessor


def _frame(synthetic):
    df = synthetic.copy()
    rng = np.random.default_rng(3)
    n = len(df)
    df["REPORTED_INCOME"] = df["HOUSEHOLD_INCOME"] * rng.uniform(0.95, 1.05, n)
    df["MONTHLY_EXPENSES"] = rng.uniform(500, 3000, n)
    df["SAVINGS_BALANCE"] = rng.uniform(0, 20000, n)
    df["CHECKING_BALANCE"] = rng.uniform(0, 5000, n)
    df["REVOLVING_UTILIZATION"] = rng.uniform(0, 1, n)
    for c in ("DELINQ_30", "DELINQ_60", "DELINQ_90", "MISSED_PAYMENTS_12M"):
        df[c] = rng.integers(0, 3, n).astype(float)
    return df


def test_features_and_weights(synthetic):
    df = _frame(synthetic)
    f = extra.add_features(df)
    new = [c for c in f.columns if c.startswith("F_")]
    assert len(new) == 7
    vals = f[new].to_numpy(float)
    assert not np.isinf(vals).any()
    y = df["DEFAULT"].to_numpy()
    w = extra.stake_weights(df, y)
    assert abs(w.mean() - 1) < 1e-9 and (w > 0).all()
    assert extra.profit_target(df, y).shape == y.shape


def test_collateral_loss_matches_mean_and_rule(synthetic):
    df = synthetic
    frac = extra.collateral_loss_fraction(df, 0.5)
    assert abs(frac.mean() - 0.5) < 0.01 and (frac >= 0.05).all() and (frac <= 1).all()
    assert np.corrcoef(frac, df["LOAN_TO_VALUE"].to_numpy())[0, 1] > 0.9
    p = np.random.default_rng(2).uniform(0.01, 0.6, len(df))
    assert extra.rule_decisions(df, p, 0.5).dtype == bool
    assert extra.rule_decisions(df, p, frac).dtype == bool


def test_weighted_oof_regressor_and_stack(synthetic):
    X, y, _ = data.split_xy(synthetic)
    X = X[config.feature_columns(synthetic.columns, "clean")]
    yy = y.to_numpy()
    w = extra.stake_weights(synthetic, yy)
    p = extra.oof_weighted(models.xgboost(X, n_estimators=30), X, yy, w, n_folds=3)
    q = extra.oof_weighted(models.logreg(X), X, yy, None, n_folds=3)
    assert p.shape == (len(yy),) and ((p >= 0) & (p <= 1)).all()
    assert extra.stack_oof([p, q], yy, n_folds=3).shape == p.shape
    reg = Pipeline([("prep", make_preprocessor(X)), ("model", XGBRegressor(n_estimators=20, max_depth=2))])
    t = extra.profit_target(synthetic, yy)
    assert extra.oof_profit_regressor(reg, X, t, yy, n_folds=3).shape == t.shape
    res = extra.summary(synthetic, yy, p=p)
    assert {"auc", "cut_0.5", "rule_0.5"} <= set(res)
    assert pytest is not None


def test_uncertainty_adjusted_pd():
    members = np.array([[0.10, 0.20, 0.90], [0.20, 0.20, 0.95], [0.30, 0.20, 1.00]])
    mean = members.mean(axis=0)
    assert np.allclose(extra.uncertainty_adjusted_pd(members, k=0), mean)
    adj = extra.uncertainty_adjusted_pd(members, k=1)
    assert adj[0] > mean[0]                      # members disagree -> more cautious
    assert adj[1] == pytest.approx(mean[1])      # members agree -> unchanged
    assert adj.max() <= 1.0                      # clipped to a probability


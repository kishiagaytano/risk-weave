import numpy as np
import pytest

from risk_weave import blend, data


def _split(synthetic):
    train = synthetic.iloc[:2200].reset_index(drop=True)
    score = synthetic.iloc[2200:2700].drop(columns=["DEFAULT"]).reset_index(drop=True)
    return train, score


def test_rule_and_profit_match_hand_calculation():
    e = {"amt": np.array([10000.0, 10000.0]), "pay": np.array([300.0, 300.0]), "gain": np.array([2000.0, 2000.0])}
    # loss = 0.7 x max(10000 - 18 x 300, 0) = 3220: approve when (1-p) x 2000 > p x 3220
    ap = blend.rule(e, np.array([0.30, 0.45]), 0.7, 18)
    assert ap.tolist() == [True, False]
    y = np.array([1, 0])
    assert blend.profit(e, y, np.array([True, True]), 0.7, 18) == pytest.approx((-3220 + 2000) / 1e6)
    assert blend.profit(e, y, np.array([True, True]), 0.7, 18, idx=np.array([1])) == pytest.approx(2000 / 1e6)


def test_accept_needs_margin_and_fold_consistency():
    base = {"auc": 0.80, "fold_auc": [0.8] * 5, "profit_main": 100.0, "fold_profit_main": [20.0] * 5}
    good = {"auc": 0.802, "fold_auc": [0.802] * 5, "profit_main": 100.0, "fold_profit_main": [20.0] * 5}
    small = {"auc": 0.8005, "fold_auc": [0.8005] * 5, "profit_main": 100.0, "fold_profit_main": [20.0] * 5}
    one_fold = {"auc": 0.802, "fold_auc": [0.81, 0.8, 0.8, 0.8, 0.8], "profit_main": 100.0, "fold_profit_main": [20.0] * 5}
    rich = {"auc": 0.80, "fold_auc": [0.8] * 5, "profit_main": 100.5, "fold_profit_main": [20.2, 20.1, 20.1, 20.1, 19.9]}
    assert blend.accept(base, good)["accepted"] and blend.accept(base, good)["by_auc"]
    assert not blend.accept(base, small)["accepted"]
    assert not blend.accept(base, one_fold)["accepted"]
    assert blend.accept(base, rich)["by_profit"]


def test_nnls_weights_are_a_distribution_and_nested_stack_is_honest():
    rng = np.random.default_rng(0)
    y = (rng.uniform(size=600) < 0.3).astype(int)
    good = np.clip(0.3 + 0.4 * (y - 0.3) + rng.normal(0, 0.1, 600), 0.01, 0.99)
    junk = rng.uniform(0.05, 0.9, 600)
    w = blend.nnls_weights(np.array([good, junk]), y)
    assert w.min() >= 0 and w.sum() == pytest.approx(1.0) and w[0] > w[1]
    folds = blend.folds_for(y, 3)
    st = blend.stacked_oof(np.array([good, junk]), y, folds)
    assert st.shape == y.shape and np.isfinite(st).all()


def test_experiment_end_to_end_on_synthetic_data(synthetic, tmp_path):
    train, score = _split(synthetic)
    res = blend.run_experiment(train, score, out_dir=tmp_path, families=("hgb_d3", "mlp"), fast=True, n_folds=3)
    assert res["base"]["auc"] > 0.6 and set(res["singles"]) >= {"lr", "xgb_d2", "xgb_d3", "hgb_d3", "mlp"}
    assert (tmp_path / "hgb_d3_clean.npy").exists() and (tmp_path / "blend_summary.json").exists()
    again = blend.run_experiment(train, None, out_dir=tmp_path, families=("hgb_d3", "mlp"), fast=True, n_folds=3)
    assert again["base"]["auc"] == pytest.approx(res["base"]["auc"])     # resumes from the saved arrays
    if res["candidate"] is not None:                                      # only when a blend passes the acceptance rule
        frame = res["candidate"]["frame"]
        assert list(frame.columns) == ["LOAN_ID", "APPROVED"] and len(frame) == len(score)


def test_candidate_builder_validates_format(synthetic):
    _, score = _split(synthetic)
    p = np.random.default_rng(3).uniform(0.02, 0.4, len(score))
    for formula in blend.FORMULAS:
        sub = blend.build_candidate(score, p, formula)
        assert sub["LOAN_ID"].is_unique and set(sub["APPROVED"].unique()) <= {0, 1}
    stacked = blend.fit_blend_scores(_split(synthetic)[0], score, {"lr": 0.5, "hgb_d3": 0.5}, fast=True)
    assert stacked.shape == (len(score),) and ((stacked > 0) & (stacked < 1)).all()

import numpy as np

from risk_weave import config, pipeline


def _split(synthetic):
    train = synthetic.iloc[:2200].reset_index(drop=True)
    score = synthetic.iloc[2200:2700].drop(columns=["DEFAULT"]).reset_index(drop=True)
    return train, score


def test_decisions_shapes_and_cutoff_monotonicity(synthetic):
    _, score = _split(synthetic)
    p = np.random.default_rng(5).uniform(0.02, 0.5, len(score))
    dec = pipeline.decisions(score, p)
    assert set(dec) == {"rule", "cut20", "cut25"}
    assert all(len(v) == len(score) and set(np.unique(v)) <= {0, 1} for v in dec.values())
    assert (dec["cut25"] >= dec["cut20"]).all()        # a higher cutoff approves a superset


def test_run_all_end_to_end_without_writing_inside_the_repo(synthetic, tmp_path, monkeypatch):
    train, score = _split(synthetic)
    monkeypatch.setattr(pipeline, "MEMBERS", {
        "lr_clean": dict(model="logreg", feature_set="clean", params=dict(C=0.1)),
        "xgb_d2_clean": dict(model="xgboost", feature_set="clean", params=dict(max_depth=2, n_estimators=30)),
    })
    res = pipeline.run_all(train, score, out_dir=tmp_path, n_folds=3, log_path=str(tmp_path / "log.jsonl"))
    assert res["audit"]["id_overlap"] == 0 and res["audit"]["schema_diff"] == ["DEFAULT"]
    assert res["cv"]["auc"] > 0.65
    assert set(res["submissions"]) == {"rule", "cut20", "cut25"}
    for sub in res["submissions"].values():
        assert list(sub.columns) == [config.ID_COL, "APPROVED"] and len(sub) == len(score)
    assert sorted(p.name for p in tmp_path.glob("cand_*.csv")) == ["cand_cut20.csv", "cand_cut25.csv", "cand_rule.csv"]
    assert (tmp_path / "log.jsonl").exists()

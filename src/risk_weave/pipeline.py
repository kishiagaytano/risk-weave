"""End-to-end orchestration of the documented solution.

During the competition each step below was run interactively inside SAS Viya for Learners
(see docs/vfl-usage.md); this module chains the same functions so the whole workflow can be
re-run with one call on any pair of train / scoring frames (the real VFL tables, or the
synthetic frames used by the tests). It does not change any modelling decision: feature set,
model hyperparameters, seeds, validation and policy are the ones recorded in
docs/experiment-log.md and docs/model-card.md.
"""
from pathlib import Path

import numpy as np

from . import config, cv, data, extra, final, metrics, models, policy, submission
from .run import run_experiment

# Cross-validated members of the final ensemble (feature set `clean`).
MEMBERS = {
    "lr_clean": dict(model="logreg", feature_set="clean", params=dict(C=0.1)),
    "xgb_d2_clean": dict(model="xgboost", feature_set="clean", params=dict(final.XGB_D2)),
    "xgb_d3_clean": dict(model="xgboost", feature_set="clean", params=dict(final.XGB_D3)),
}
LOSS_FRACTION = 0.5          # loss share of LOAN_AMOUNT in the per-loan rule (fitted to public scores)
CUTOFFS = (0.20, 0.25)       # single-cutoff probes kept as the hedge file


def cross_validate(train, n_folds=config.N_FOLDS, log_path=None):
    """5-fold OOF for each member; returns the raw averaged OOF probability and its summary."""
    oofs = []
    for name, spec in MEMBERS.items():
        _, oof, _ = run_experiment(train, name, spec, env="pipeline", n_folds=n_folds, log_path=log_path)
        oofs.append(oof)
    p = np.mean(oofs, axis=0)
    y = train[config.TARGET].to_numpy()
    return p, {
        "auc": metrics.summarise(y, p)["auc"],
        "profit": extra.summary(train, y, p=p),
    }


def decisions(df, pd_scores, loss_fraction=LOSS_FRACTION, cutoffs=CUTOFFS):
    """Decision vectors: the per-loan expected-profit rule and the single PD cutoffs."""
    out = {"rule": extra.rule_decisions(df, pd_scores, loss_fraction).astype(int)}
    for t in cutoffs:
        out[f"cut{int(round(t * 100)):02d}"] = (np.asarray(pd_scores) < t).astype(int)
    return out


def run_all(train, score, out_dir=None, n_folds=config.N_FOLDS, log_path=None):
    """Audit -> cross-validate -> final fit -> decisions -> validated submission frames.

    Returns a dict with the audit, CV summary, scoring PDs and the submission frames. When
    ``out_dir`` is given the validated files are written there (never inside the repository:
    submission files are not committed, see docs/submission-checksums.md).
    """
    audit = data.audit(train, score)
    oof, cv_summary = cross_validate(train, n_folds=n_folds, log_path=log_path)
    pd_scores, _ = final.fit_predict(train, score, "clean")
    subs = {}
    for name, dec in decisions(score, pd_scores).items():
        sub = submission.build(score[config.ID_COL], dec)
        submission.validate(sub, score[config.ID_COL])
        subs[name] = sub
        if out_dir is not None:
            path = Path(out_dir)
            path.mkdir(parents=True, exist_ok=True)
            sub.to_csv(path / f"cand_{name}.csv", index=False)
    return {
        "audit": audit,
        "cv": cv_summary,
        "oof": oof,
        "score_pd": pd_scores,
        "approval": {k: float(v["APPROVED"].mean()) for k, v in subs.items()},
        "submissions": subs,
    }

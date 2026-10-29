# Documentation index

## Reading order
1. [`../README.md`](../README.md): landing page, results at a glance, quick start.
2. [`SOLUTION.md`](SOLUTION.md): the solution for judges (one page plus detail).
3. [`fairness-and-explainability.md`](fairness-and-explainability.md): group outcomes, excluded variables, coefficients, limitations.
4. [`vfl-usage.md`](vfl-usage.md): what ran inside SAS Viya for Learners and how to re-run it.
5. [`model-card.md`](model-card.md): data, features, model, validation, policy, limitations.
6. [`experiment-log.md`](experiment-log.md): every experiment with metrics (chronological).
7. [`submission-ledger.md`](submission-ledger.md) and [`submission-checksums.md`](submission-checksums.md): candidate files, public scores, SHA-256.
8. Source material: [`competition-rules-and-evaluation.md`](competition-rules-and-evaluation.md),
   [`sas-viya-observations.md`](sas-viya-observations.md), [`sas-viya-commands.sas`](sas-viya-commands.sas).

## Current status (single source of truth)
* Final model: clean 57-column ensemble (logistic regression + XGBoost depth 2 + depth 3), per-loan expected-profit
  rule with loss fraction 0.5. Cross-validated AUC 0.7987.
* Best public score 54.429 (`cand_clean_rule50`); suggested finals `cand_clean_rule50` and `cand_clean_t25` (54.290).
  The final selection is made by the participant on Kaggle.
* Older statements in the model card and ledger that mention the `no_rate` ensemble or the 0.07 / 0.12 / 0.20 cutoff
  candidates describe earlier stages and are kept for history.

## Change history (newest first)
| Date | Change |
|---|---|
| 2026-10-29 | Solution summary, VFL usage, fairness/explainability report, README rewrite, pipeline module, CI, pinned requirements, checksums |
| 2026-10-29 | Seed bagging, further optimisation experiments (none improved the final policy), probes rule50 / t28 / bag recorded |
| 2026-10-28 | Per-loan expected-profit rule, probes t07-t25, integer-ID fix, candidate ledger |
| 2026-10-28 | Pipeline, baselines, tuning, `clean` feature set, Model Studio baseline |
| 2026-10-28 | SAS Viya data audit, rules and evaluation notes |

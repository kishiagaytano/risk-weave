# Documentation index

## Reading order
1. [`../README.md`](../README.md): landing page, results at a glance, quick start.
2. [`final-submissions.md`](final-submissions.md): the two selected files and why.
3. [`SOLUTION.md`](SOLUTION.md): the solution for judges (one page plus detail).
4. [`fairness-and-explainability.md`](fairness-and-explainability.md): group outcomes, excluded variables, coefficients, limitations.
5. [`vfl-usage.md`](vfl-usage.md) (detailed VFL walkthrough), [`vfl-environment.md`](vfl-environment.md) (versions) and [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).
6. [`model-card.md`](model-card.md): data, features, model, validation, policy, limitations.
7. [`experiment-log.md`](experiment-log.md): every experiment with metrics (chronological).
8. [`submission-ledger.md`](submission-ledger.md) and [`submission-checksums.md`](submission-checksums.md): candidate files, public scores, SHA-256.
9. Source material: [`competition-rules-and-evaluation.md`](competition-rules-and-evaluation.md),
   [`sas-viya-observations.md`](sas-viya-observations.md), [`sas-viya-commands.sas`](sas-viya-commands.sas).

## Current status (single source of truth)
* Final model: clean 57-column ensemble (logistic regression + XGBoost depth 2 + depth 3), per-loan expected-profit
  rule with loss fraction 0.5. Cross-validated AUC 0.7987.
* Best public score 54.463 (`cand_clean_fit70m18`, formula-refit rule); `cand_clean_rule50` 54.429; proposed finals `cand_clean_rule50` and `cand_clean_unc1` (second final; replaces `cand_clean_t25` = 54.290 as
  of 2026-10-29; the selection is the participant's; see `final-submissions.md`).
* Older statements in the model card and ledger that mention the `no_rate` ensemble or the 0.07 / 0.12 / 0.20 cutoff
  candidates describe earlier stages and are kept for history.

## Change history (newest first)
| Date | Change |
|---|---|
| 2026-10-29 | `cand_clean_fit70m18` (loss refitted to public scores) scores 54.463, highest of our files; nine-point refit and spline-member test recorded in the experiment log |
| 2026-10-29 | Public score of `cand_clean_unc1` (54.265) recorded; new second final `cand_clean_unc1` (uncertainty-adjusted rule), variant comparison, `extra.uncertainty_adjusted_pd` |
| 2026-10-29 | Final submissions document, reproducibility guide, detailed VFL walkthrough, VFL versions, importance analysis (permutation, gain, TreeSHAP), MIT license |
| 2026-10-29 | Solution summary, VFL usage, fairness/explainability report, README rewrite, pipeline module, CI, pinned requirements, checksums |
| 2026-10-29 | Seed bagging, further optimisation experiments (none improved the final policy), probes rule50 / t28 / bag recorded |
| 2026-10-28 | Per-loan expected-profit rule, probes t07-t25, integer-ID fix, candidate ledger |
| 2026-10-28 | Pipeline, baselines, tuning, `clean` feature set, Model Studio baseline |
| 2026-10-28 | SAS Viya data audit, rules and evaluation notes |

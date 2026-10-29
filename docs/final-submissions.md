# Final submissions and why

Two files are selected for final scoring. Both come from the same model; they differ only in the decision rule.

| | `cand_clean_rule50` | `cand_clean_t25` |
|---|---|---|
| Decision rule | Approve when `(1 - PD) x interest earned > PD x 0.5 x loan amount` | Approve when `PD < 0.25` |
| Approved | 82.47% | 84.43% |
| Public score (40% of test rows) | **54.429** (best of all probes) | 54.290 (best single cutoff) |
| SHA-256 | `2189c097ee2aa222599fc6d730e0ba696f64567ed3248d717c8f1f7b07670cd0` | `99315129c12c38173e8657f6658236fb0a859162393dc5d92324ee01bb6d7d63` |
| Role | Primary: principled expected-profit policy | Hedge: plain risk cutoff, fails differently |

The choice was made by the participant on 2026-10-29 from the candidates in `submission-ledger.md`.
The selection click on Kaggle is the participant's own.

## 1. What the competition asks for, and how each file answers it

Source: `competition-rules-and-evaluation.md` (rules as read from the Overview/Evaluation pages).

| Requirement | How the submission meets it |
|---|---|
| File format: `LOAN_ID,APPROVED`, one row per scoring loan, 1 = approve | Built and validated by `risk_weave.submission` (100,000 rows, unique integer IDs matching the scoring table, values 0/1). Float IDs were found and fixed before any upload. |
| Profit | The decision rule is an explicit expected-profit comparison; the model estimates default risk from 57 credit attributes (cross-validated AUC 0.7987, well calibrated). Public score 54.429. |
| Risk management | Declined loans default at 38.0% versus 8.2% among approved loans (out-of-fold); the rule approves a loan only when its interest income covers its expected loss, so risky loans are approved only when they pay for the risk. |
| Access to credit | 82.5% approval overall; the 0.07 and 0.12 cutoffs (44% / 63% approval) were rejected both on score and on access. |
| Fairness | No race/ethnicity, gender, age, marital status or proxy-prone fields in the model; group outcomes in `fairness-and-explainability.md` (default among approved 6.2-10.2% for all levels; disclosed approval gaps). |
| Explainability | Logistic-regression coefficients, permutation importance, XGBoost gain and native TreeSHAP (computed in VFL; the `shap` package was not used), and a one-line dollar reason for each rule approval (`fairness-and-explainability.md`). |
| Use of SAS Viya for Learners | Data access, modelling, final fit, scoring and Model Studio baseline all ran in VFL (`vfl-usage.md`, `vfl-environment.md`). |
| Reproducible documentation | `REPRODUCIBILITY.md`; tests, pinned requirements, recorded VFL versions, checksums, experiment log. |

## 2. Why the rule file is the primary

* It is the only policy whose logic is a stated business rule rather than a tuned number: approve when expected
  interest exceeds expected loss.
* Under the fitted profit model it has the highest cross-validated profit (121.0 $M versus 120.8 for cutoff 0.25) and
  the highest public score.
* It beat each single cutoff (0.25, 0.20, 0.28, 0.16) on 100% of 400 random 60% resamples of out-of-fold data
  (mean margin +0.57 $M against 0.25 up to +2.99 against 0.16, standard deviation 0.18 for the closest rival).
* Its loss fraction (0.5) was inferred from public scores, not given; this is stated as a limitation, and it is the
  reason a second, differently-structured file is also selected.

## 3. Why `t25` is the second

* It is the best-scoring single-cutoff file (54.290), so the pair is not two near-copies of one idea.
* It is robust if the hidden metric weights loan size or loss differently from the fitted formula: a pure risk
  cutoff does not depend on the interest or loss assumption at all.
* It approves 2 points more loans (better access) at a profit cost of about 0.2% under the fitted formula.
* Both files agree on most loans: they differ where a loan's size or interest moves it across the break-even line.

## 4. What was not selected and why

| File | Public | Reason not selected |
|---|---|---|
| `cand_clean_rule50_bag` (10-seed average) | 54.370 | Statistically indistinguishable from rule50 (0.62% of decisions differ, seed spread +-0.1 $M); not better, so not preferred. |
| `cand_clean_t20` | 53.935 | Lower score and lower approval (78.6%). |
| `cand_clean_t28` | 53.924 | Lower score; 87% approvals raise default exposure. |
| `cand_clean_t12`, `t07` | 47.159, 34.812 | Over-restrictive; used as probes to infer the metric. |

## 5. Public versus private scores

The public score uses 40% of the test rows; the final ranking uses the other 60%. Differences below about 1 point are
within sampling noise (estimated sd about 1.0), so the selection did **not** rely on small public gaps: the choice
rests on the principled rule, cross-validated profit on all 100,000 labelled loans, and resampling checks.
No model hyper-parameters or random seeds were chosen using the public leaderboard; the public scores were used only
to infer the shape of the metric (loss fraction) and to rank decision rules.

## 6. Reproducing the two files

1. Install the package in VFL and run `pipeline.run_all` (see `vfl-usage.md` and `REPRODUCIBILITY.md`).
2. Compare SHA-256 values to `submission-checksums.md`. The default seed is 20261028; the same VFL package versions
   (`vfl-environment.md`) are required for byte-identical files. The submitted files themselves are not committed
   (competition rules); only checksums are.

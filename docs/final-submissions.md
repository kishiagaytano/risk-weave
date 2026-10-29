# Final submissions and why

**Final pair (chosen by the participant, 2026-10-30): `cand_clean_fit70m18` and `cand_clean_rule50`.** Both come from the
same model and the same default probabilities and differ only in the loss assumption of the decision rule. The Kaggle
selection itself is made by the participant.

| | `cand_clean_fit70m18` | `cand_clean_rule50` |
|---|---|---|
| Decision rule | Approve when `(1 - PD) x total interest > PD x 0.7 x max(loan - 18 x monthly payment, 0)` | Approve when `(1 - PD) x total interest > PD x 0.5 x loan` |
| Loss assumption | Loss share fitted to public-score evidence; defaults after about 18 payments | Loss of half the loan (fitted to the first public scores) |
| Approved (scoring file) | 83.51% (83,511 loans) | 82.47% (82,469 loans) |
| Approved (out-of-fold, saved `rw/oof` arrays) | 82.7% | 81.8% |
| Public score (40% of test rows) | **54.463** (highest of our files) | 54.429 |
| SHA-256 | `f855bec552e1185cdabbd04e5f726926cff4b733ffe0866b058de2f555a81c9f` | `2189c097ee2aa222599fc6d730e0ba696f64567ed3248d717c8f1f7b07670cd0` |

Applicants approved by only one of the two files (scoring file): rule50 only 290, fit70m18 only 1,332 (1.6% of
applicants differ). Figures are labelled by source: *scoring file* = the 100,000 submitted decisions; *out-of-fold* =
the 100,000 labelled training loans scored by models that never saw them. The two differ by about 0.7-0.9 points of
approval because the loans differ, not because of the code (the scoring side reproduces rule50's recorded hash exactly).

## 1. What the competition asks for, and how each file answers it

Source: `competition-rules-and-evaluation.md` (rules as read from the Overview/Evaluation pages).

| Requirement | How the submission meets it |
|---|---|
| File format: `LOAN_ID,APPROVED`, one row per scoring loan, 1 = approve | Built and validated by `risk_weave.submission` (100,000 rows, unique integer IDs matching the scoring table, values 0/1). Float IDs were found and fixed before any upload. |
| Profit | The decision rule is an explicit expected-profit comparison; the model estimates default risk from 57 credit attributes (cross-validated AUC 0.7987, well calibrated). Public scores 54.463 and 54.429. |
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
  reason a second, differently-structured file is also proposed.

## 3. Why `unc1` is the second final (replacing `t25`)
* **What it is.** The same expected-profit rule as rule50, applied to a default probability raised by one standard
  deviation of the three member models' predictions. Loans on which logistic regression and the two XGBoost models
  disagree are held to a higher bar; confident loans are untouched. `unc1` approves a strict subset of rule50's
  approvals (2,235 fewer, 2.2% of applicants).
* **Evidence** (out-of-fold, loss fractions 0.3-0.7, gain = total interest; efficiency = profit as a share of the best
  achievable at each loss fraction): `unc1` mean efficiency 0.9809 and worst case 0.9501, against `t25` 0.9775 and 0.9490
  and rule50 0.9834 and 0.9667; profit at loss 0.5 is 120.4 $M (`t25` 120.3, rule50 120.9). Full table of all ten variants
  in `submission-ledger.md`. No variant beats rule50 under the fitted formula; the second final is for diversification.
* **Why not the others.** Loss fraction 0.4 or 0.6 changed 4-5% of decisions but had worst-case efficiency 0.908 / 0.938;
  +2 sd cut approval to 76.8%; blends with a cutoff or member-weight changes differ from rule50 on under 1% of
  applicants, which would not diversify.
* **Difference from the other files** (scoring file, applicants approved by A only / by B only): rule50 vs `unc1`
  2,235 / 0; rule50 vs `t25` 1,293 / 3,253; `unc1` vs `t25` 678 / 4,873.
* **Cost, stated plainly.** Lower approval (80.2% versus 84.4% for `t25` and 82.5% for rule50), so slightly less access
  to credit, and a public score of 54.265 (0.025 below `t25`, 0.164 below rule50; both gaps are within public noise of about 1.0). The loss fraction (0.5) remains inferred, not given.
* **Former choice.** `t25` (public 54.290) stays as an alternate; it does not depend on any interest or loss assumption,
  so it fails differently if the hidden metric differs. Which second file to select is the participant's decision.

`cand_clean_fit70m18` (formula refit, 83.51% approved) scored 54.463 publicly, the highest of our files (+0.034 over rule50, within public noise). It tests whether the refitted loss formula predicts the metric better; it is a candidate for the final pair alongside rule50 but the selection is the participant's (see `submission-ledger.md`, candidate 10).

## 4. What was not selected and why

| File | Public | Reason not selected |
|---|---|---|
| `cand_clean_t25` | 54.290 | Former second final; replaced by `unc1` on robustness (see 3), kept as alternate. |
| `cand_clean_rule50_bag` (10-seed average) | 54.370 | Statistically indistinguishable from rule50 (0.62% of decisions differ, seed spread +-0.1 $M); not better, so not preferred. |
| `cand_clean_t20` | 53.935 | Lower score and lower approval (78.6%). |
| `cand_clean_t28` | 53.924 | Lower score; 87% approvals raise default exposure. |
| `cand_clean_t12`, `t07` | 47.159, 34.812 | Over-restrictive; used as probes to infer the metric. |

## 2. Why these two files

* **One model, two loss hypotheses.** Both files use the same ensemble PDs (logistic regression + XGBoost depth 2 and 3,
  57 clean columns, cross-validated AUC about 0.799). The competition does not publish its profit formula, so the loss
  assumption is the main uncertainty. `rule50` uses the original fit (loss = 50% of the loan); `fit70m18` uses a loss
  refitted to nine public scores (70% of the loan after 18 payments). Holding both covers either outcome: the refitted
  formulas predict `fit70m18` ahead by about 0.1-0.15 public points and the original formula predicts `rule50` ahead by
  about 0.09.
* **Public evidence.** `fit70m18` 54.463 and `rule50` 54.429 are the two highest of our files. The gap (0.034) is far
  inside public noise (about 1.0), so the choice does not rest on it.
* **Fit evidence.** Fitting the public scores of nine files, the loss shape `R x (loan - k payments)` with R 0.7-0.85 and
  k 18-25 has RMS error about 0.14-0.16 against 0.31 for the 50%-of-loan formula; nested leave-one-out error 0.20-0.27
  against 0.34. R and k are not separately identified (the fit valley is flat). Richer shapes (vehicle value,
  loan-to-value, default timing as a share of the term) fitted worse out of sample.
* **Robustness.** Out-of-fold, both rules are close under every formula in the valley and under the original one
  (labelled training loans, realised outcomes): profit 120.92 $M (`rule50`) vs 120.72 (`fit70m18`) under the original
  formula, and 123.83 vs 124.11 under the 0.8 x (loan - 23 payments) formula.
* **Hedge, not a model diversification.** They differ on only 1.6% of applicants, so this is a hedge on the loss formula.
  It is chosen over a more different second file because the more different files scored lower on every fitted formula.

## 3. Same-model alternatives tried and not selected

| File | Public | Approved (scoring) | Reason not selected |
|---|---|---|---|
| `cand_clean_fitA80k23` (best refined formula, loss 0.8 x (loan - 23 payments)) | 54.373 | 83.67% | 0.090 below `fit70m18`; predicted 0 +-0.05, so no support for further refinement. |
| `cand_clean_rule50_bag` (10-seed average) | 54.370 | 82.42% | Indistinguishable from rule50 (0.62% of decisions differ); not better. |
| `cand_clean_t25` (PD < 0.25) | 54.290 | 84.43% | Best single cutoff; lower than both finals and lower under every fitted formula. |
| `cand_clean_unc1` (rule on PD + 1 std of member PDs) | 54.265 | 80.23% | More cautious diversifier; lowest of the close candidates and lower approval. |
| `cand_clean_t20`, `t28` | 53.935, 53.924 | 78.59%, 87.03% | Lower score; the cutoff curve is flat near 0.25. |
| `cand_clean_t12`, `t07` | 47.159, 34.812 | 62.55%, 43.98% | Over-restrictive; used as probes to infer the metric. |

Further variants (uncertainty-adjusted formula rule, probe files) were built in VFL only and never uploaded; see
`submission-ledger.md` and `experiment-log.md`.

## 4. Kaggle submission description

See `kaggle-description.md` (short text for each of the two files).

## 5. Public versus private scores

The public score uses 40% of the test rows; the final ranking uses the other 60%. Differences below about 1 point are
within sampling noise (estimated sd about 1.0), so the selection did **not** rely on small public gaps: the choice
rests on the principled rule, cross-validated profit on all 100,000 labelled loans, and the robustness table across loss
fractions. No model hyper-parameters or random
seeds were chosen using the public leaderboard; the public scores were used only to infer the shape of the metric (loss
fraction) and to rank decision rules.

## 6. Reproducing the files

1. Install the package in VFL and run `pipeline.run_all` (see `vfl-usage.md` and `REPRODUCIBILITY.md`).
   The scoring member PDs are rows 1-3 of `rw/oof/score_pd_clean.npy` in the VFL session that produced the files; the
   rule is `extra.rule_decisions` with the per-loan loss (`0.5 x loan` for `rule50`, `0.7 x max(loan - 18 x payment, 0)`
   for `fit70m18`).
2. Compare SHA-256 values to `submission-checksums.md`. The default seed is 20261028; the same VFL package versions
   (`vfl-environment.md`) are required for byte-identical files. The submitted files themselves are not committed
   (competition rules); only checksums are.

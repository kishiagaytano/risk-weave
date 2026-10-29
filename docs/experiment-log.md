# Experiment log (VFL, full 100K training rows)

> Chronological record. Final model and policy: see `SOLUTION.md`. Earlier sections (for example the `no_rate` ensemble)
> are superseded by the `clean` feature set but are kept unchanged for history.


All runs: Python in SAS Studio on `CREDITr.ILINK_CREDITRISK_TRAINING`, 5-fold
stratified CV, seed 20261028, out-of-fold (OOF) predictions. Calibration is an
isotonic fit cross-fitted on the OOF scores. Machine-readable records live in
`~/rw/experiment_log.jsonl` on the VFL compute server (not committed; it only
contains aggregate metrics). Primary feature set = all columns except `LOAN_ID`,
`DEFAULT` and the five sensitive columns (`RACE_ETH`, `GENDER`, `AGE_BAND`,
`AGE_D`, `MARITAL_STATUS`).

Metrics are on raw OOF scores. `thr`/`approval` come from the robust-threshold
search in `policy.py` (see "Policy" below).

| Run | Feature set | Model | AUC | PR-AUC | KS | Logloss |
|---|---|---|---|---|---|---|
| lr_primary | primary | L2 logistic regression, C=0.1 | 0.7986 | 0.4246 | 0.4493 | 0.3210 |
| xgb_primary | primary | XGBoost depth 4, 400 trees | 0.7977 | 0.4223 | 0.4465 | 0.3215 |
| lr_no_rate | no INTEREST_RATE | logistic regression | 0.7975 | 0.4232 | 0.4454 | 0.3215 |
| xgb_no_rate | no INTEREST_RATE | XGBoost depth 4 | 0.7972 | 0.4207 | 0.4463 | 0.3219 |
| xgb_with_sensitive | primary + sensitive | XGBoost depth 4 | 0.7982 | 0.4227 | 0.4495 | 0.3213 |
| xgb_d2 | primary | XGBoost depth 2, 800 trees, lr 0.05 | 0.7990 | 0.4247 | 0.4499 | 0.3206 |
| xgb_d3 | primary | XGBoost depth 3, 500 trees, lr 0.04, mcw 20, lambda 10 | 0.7990 | 0.4244 | 0.4507 | 0.3208 |
| xgb_d6 | primary | XGBoost depth 6, 400 trees, lr 0.02, subsample 0.7 | 0.7987 | 0.4231 | - | 0.3211 |
| lr_spline | primary | logistic regression with cubic splines (5 knots) | 0.7990 | 0.4256 | 0.4489 | 0.3208 |

Blends (equal-weight average of OOF probabilities):

| Blend | AUC | PR-AUC |
|---|---|---|
| lr_primary + xgb_primary | 0.7997 | 0.4265 |
| lr_primary + xgb_d2 | 0.8002 | 0.4270 |
| lr_primary + xgb_d3 | 0.8002 | - |
| lr_primary + xgb_d2 + xgb_d3 | 0.8003 | 0.4271 |
| lr_primary + xgb_primary + xgb_d3 | 0.7999 | 0.4267 |
| lr_spline + xgb_d2 + xgb_d3 | 0.8000 | 0.4268 |
| lr_spline + lr_primary + xgb_d2 + xgb_d3 | 0.8003 | 0.4275 |

## Findings

- Logistic regression is as good as XGBoost; spline-LR equals shallow XGBoost.
  The signal is smooth and mostly additive. Deeper trees (depth 6) do not help.
- `INTEREST_RATE` adds about 0.001 AUC (LR 0.7986 vs 0.7975; XGBoost 0.7977 vs
  0.7972), so it is largely a function of other fields.
- The five excluded sensitive columns add about 0.0005 AUC (XGBoost 0.7982 with
  vs 0.7977 without): excluding them is nearly free.
- Equal-weight blends add about +0.0013 to +0.0017 AUC over the best single model;
  variants differ by less than 0.0005, so CV has stopped improving. Fold-to-fold
  AUC standard deviation is about 0.002, so single-run differences below that are
  noise.
- A random-forest/extra-trees run was not made: boosted trees and LR already
  agree to the fourth decimal, so a weaker tree ensemble is unlikely to add value.

## Operational notes

- The CAS libref can be lost between runs (`sd2df` then returns an empty
  frame); `data.load_vfl` now re-assigns it.
- Typing code into the SAS Studio editor is unreliable (auto-indent, long-line
  wrapping), so the package is installed in the VFL home through
  `tools/pack_for_vfl.py`, which encodes exactly the repo code.

## No-INTEREST_RATE tuned models and ensemble (feature set `no_rate`)

| Run | AUC (raw OOF) |
|---|---|
| lr_no_rate | 0.7975 |
| xgb_no_rate (depth 4) | 0.7972 |
| xgb_d2_norate / xgb_d3_norate | recorded in `~/rw/experiment_log.jsonl` (about 0.798-0.799) |

Final candidate ensemble = equal-weight mean of `lr_no_rate`, `xgb_d2_norate`,
`xgb_d3_norate`. After cross-fitted isotonic calibration its OOF AUC is 0.798 and
logloss 0.3212 (the isotonic step slightly reduces AUC through ties; raw
probabilities are already well calibrated, ECE about 0.001-0.002, so decisions
use the raw averaged probability).

## Policy sensitivity (OOF, raw ensemble probability, profit in $M over 100K loans)

Approve when predicted PD < t. Eight documented scenarios: gain if repaid =
total scheduled interest (`tot`, MONTHLY_PAYMENT x LOAN_TERM - LOAN_AMOUNT) or
one year of interest (`one`, LOAN_AMOUNT x INTEREST_RATE); loss if default =
LGD x LOAN_AMOUNT. These are assumptions, not the official formula.

| Scenario (gain, LGD) | t=0.05 | 0.07 | 0.10 | 0.12 | 0.15 | 0.20 | 0.30 |
|---|---|---|---|---|---|---|---|
| tot 0.3 | 64.1 | 85.5 | 109.2 | 119.8 | 131.5 | 143.0 | 150.6 |
| tot 0.5 | 60.4 | 78.9 | 98.5 | 106.4 | 114.2 | 119.9 | 118.3 |
| tot 0.7 | 56.6 | 72.4 | 87.9 | 93.0 | 96.8 | 96.8 | 86.0 |
| tot 1.0 | 51.0 | 62.7 | 72.0 | 72.9 | 70.8 | 62.3 | 37.5 |
| one 0.3 | 23.0 | 25.9 | 30.2 | 31.2 | 31.2 | 29.3 | 22.5 |
| one 0.5 | 17.2 | 19.4 | 19.6 | 17.8 | 13.9 | 6.3 | -9.9 |
| one 0.7 | 13.5 | 12.9 | 9.0 | 4.3 | -3.5 | -16.8 | -42.2 |
| one 1.0 | 7.9 | 3.1 | -7.0 | -15.8 | -29.5 | -51.4 | -90.6 |

Approval rate at t=0.07 is 43.8% on OOF. The best cutoff per scenario ranges from
0.04 to 0.38, so the official formula decides the cutoff. t=0.07 is the most
defensive choice (never loses money in the grid); t=0.12 is a mid-point that
keeps most of the upside when gains are total interest and losses are at most
half the principal; t=0.20 is aggressive.

## Group outcomes at t=0.07 (OOF, sensitive columns not used as inputs)

| Group | Approval rate by level | Default rate among approved |
|---|---|---|
| RACE_ETH | Asian .46, Black .39, Hispanic .42, Other .43, White .46 | .032 / .037 / .039 / .033 / .035 |
| GENDER | Female .44, Male .44, Nonbinary .44 | .036 / .034 / .044 |
| AGE_BAND | 18-29 .395, 30-44 .44, 45-59 .45, 60+ .44 | .038 / .037 / .034 / .029 |
| MARITAL_STATUS | Married .44, Single .43 | .036 / .035 |
| STATE_TIER | H .56, M .45, L .31 | .034 / .035 / .040 |

Approved-loan default rates are similar across groups (calibration holds), but
approval rates differ: Black applicants 0.39 vs White 0.46 (ratio about 0.84) and
state tier L 0.31 vs H 0.56 (ratio about 0.55). These gaps reflect genuine
default-rate differences in the data; they are reported, not corrected.

## Sensitivity: proxy and timing fields, and the `clean` feature set

| Run | Columns | AUC (raw OOF) | Logloss |
|---|---|---|---|
| xgb_primary (reference) | 76 | 0.7977 | 0.3215 |
| xgb_no_proxy (14 proxy-capable fields removed) | 62 | 0.7975 | 0.3216 |
| xgb_no_timing (PREVIOUS_*/CREDIT_BUILDER/CREDIT_MONITORING removed) | 72 | 0.7979 | 0.3215 |
| xgb_d3_clean | 57 | 0.7975 | 0.3215 |
| xgb_d2_clean / lr_clean | 57 | about 0.798 / about 0.797 | recorded in `~/rw/experiment_log.jsonl` |
| **clean ensemble (LR + XGB d2 + XGB d3, raw mean)** | 57 | **0.7987** (PR-AUC 0.425) | - |

Removing the proxy-capable and timing-uncertain fields costs at most 0.0002 AUC,
so they carry no measurable signal here. The `clean` ensemble loses about 0.001
AUC against the `no_rate` ensemble (0.7987 vs 0.800) and keeps the same policy
profile (approval 32.7% / 43.7% / 56.3% at t = 0.05 / 0.07 / 0.12; profit table
within about 1 percentage point of the `no_rate` ensemble). Group outcomes at
t=0.07 are unchanged (approval: White .46, Asian .46, Hispanic .42, Black .38;
state tier H .57, L .31). Final-fit predictions of the two ensembles on the scoring
table correlate at 0.995 and give identical decisions for 97.3% of applicants.
**Recommended feature set for the final model: `clean`.**

## Model Studio baseline (comparison only)

Project `RiskWeave_Baseline` in SAS Model Studio (VFL, My Folder) on
`CREDITr.ILINK_CREDITRISK_TRAINING`. Target `DEFAULT`; the 25 fields of the
`clean` exclusion (five sensitive columns, `INTEREST_RATE`, 14 proxy-capable
fields, 4 timing-uncertain flags, plus `STATE` which Model Studio rejects by
default; `LOAN_ID` as ID) have role Rejected. Pipeline: Data -> Gradient Boosting
and Logistic Regression (stepwise), default settings, default Model Studio
partition; Model Comparison selects by KS on the Test partition (10,000 rows,
cutoff 0.50).

| Model | KS (Youden) | Accuracy | F1 at 0.50 |
|---|---|---|---|
| Gradient Boosting (champion) | 0.3686 | 0.8652 | 0 (no applicant scored above 0.50) |
| Logistic Regression (stepwise) | 0.3615 | 0.8732 | 0.2134 |

These numbers are not directly comparable with the Python cross-validation: they
use a single 10K test split, Youden KS at a 0.50 cutoff, untuned defaults (the
default gradient-boosting early stopping optimises misclassification rate), and
no calibration or profit policy. They confirm the same ordering as the Python work
(boosting and logistic regression about equal) and that the signal is
concentrated in revolving utilisation, debt-to-income, missed payments and down
payment (top Model Studio importances). The Python ensemble remains the
candidate; Model Studio is the documented reference baseline.

## Per-loan expected-profit rule vs a single cutoff (analysis, 2026-10-28)

Question: after the public scores (best 54.290 at cutoff 0.25, rank 26; leader 55.092),
does approving each loan when `(1 - PD) x gain_i > PD x loss_i` beat one global PD
cutoff? Here gain_i = total scheduled interest (`MONTHLY_PAYMENT x LOAN_TERM -
LOAN_AMOUNT`) and loss_i = fraction x `LOAN_AMOUNT`, the scenario that matched the public
scores. `LOAN_AMOUNT`, `LOAN_TERM`, `MONTHLY_PAYMENT` are used only in the decision
rule, not as model inputs. Clean-ensemble out-of-fold PD; profit in $M over 100K loans.

| Rule built with loss fraction | Approval (OOF) | profit if true loss = 0.40 | 0.45 | 0.50 | 0.55 |
|---|---|---|---|---|---|
| 0.40 | 86.8% | 135.1 | 127.4 | 119.6 | 111.9 |
| 0.45 | 84.5% | 135.0 | 127.9 | 120.7 | 113.5 |
| 0.50 | 82.3% | 134.3 | 127.6 | 121.0 | 114.3 |
| 0.55 | about 80% | 133.1 | 126.9 | 120.7 | 114.5 |
| best single cutoff (tuned per true loss) | about 0.26-0.29 | 134.5 | 127.0 | about 120.8 | about 114.3 |

- Gain of the per-loan rule over the best single cutoff is tiny: about +0.2 on 121
  (0.2%) when the loss fraction is guessed right, and a mismatch of 0.05 costs
  at most about 0.3-0.5. It is not the missing 1.5% to the leader. Predicted public
  score for the loss-0.5 rule with the fitted factor (0.443-0.450): about 54.4-54.6
  (cutoff 0.25 gave 54.290); approval on the scoring table 82.5%.
- Calibration where the decision matters is good (predicted vs observed default):
  0.15-0.20: 0.173 vs 0.171; 0.20-0.25: 0.223 vs 0.235; 0.25-0.30: 0.274 vs 0.277;
  0.30-0.35: 0.324 vs 0.323; 0.35-0.40: 0.374 vs 0.356; above 0.40: 0.546 vs 0.551.
- Feature choices barely move profit: at loss 0.5 the best single-cutoff profit is
  about 120.3-120.6 for the clean, no-rate and with-sensitive models and 120.2 for the
  with-rate ensemble (AUC 0.7987-0.8003), i.e. within 0.3%. Excluded variables
  therefore cost almost nothing and are not the reason for the gap.
- Group approval rates of the loss-0.5 rule differ by group as before (state tier H
  about 0.89 vs L lower; race and employment groups differ moderately); no
  group-level correction was applied.
- Noise: the standard deviation of a ~45K-loan public profit sum is about 1.0 ($M) for
  one policy, so a 0.8 gap to the leader is within what the public/private sampling
  alone can produce; only part of it cancels when two policies share loans.
- Candidate file `cand_clean_rule50.csv` (per-loan rule, loss 0.5, clean model,
  approval 82.47%, 100,000 unique integer IDs) was generated in VFL; not downloaded,
  not uploaded.

## Further optimisation attempts (2026-10-29): none beats the per-loan rule

All out-of-fold on the full 100K training rows in VFL, same 5-fold CV and seed, clean 57
model features (sensitive, proxy, timing-uncertain and pricing fields excluded). Profit in
$M under a true loss of 40% / 50% / 60% of the loan (gain = total scheduled interest).
Baseline = clean ensemble (LR + XGB d2 + XGB d3) with the per-loan rule at loss 0.5
("rule50", public 54.429): 135.1 / 121.0 / 108.8 (best single cutoff 134.6 / 120.3 / 108.3;
AUC 0.7987). Decision rows (`dec`) evaluate fixed decisions.

| Idea | Result (40 / 50 / 60) | vs rule50 at loss 0.5 |
|---|---|---|
| Stacking (logistic meta-learner on base logits) | rule 135.1 / 121.0 / 108.7, AUC 0.7987 | 0.0 |
| Profit-aware XGBoost (regress realised profit, approve if > 0) | 133.2 / 119.9 / 106.7 (ap 81.6%) | -1.1 |
| Collateral-aware loss (loss fraction rises with LTV, mean 0.5, sd 0.083) | flat-0.5 truth 120.5; collateral truth 119.6 (flat rule 119.1) | -0.5 / +0.5 |
| Stake-weighted XGBoost (weights = interest if repaid, 0.5 x amount if default) | 134.0 / 120.6 / 107.2 | -0.4 |
| Stake-weighted logistic regression | 134.1 / 120.8 / 107.4 | -0.2 |
| Blend of the two stake-weighted models | 134.4 / 121.1 / 107.7 | +0.1 (noise) |
| 7 engineered ratio/interaction features (XGB d3 / LR AUC 0.7975 / 0.7974 vs 0.7975 / 0.797) | blend rule 135.1 / 120.9 / 108.5 vs same blend without them 135.1 / 121.0 / 108.8 | -0.1 |

Engineered features: income gap (reported vs household), loan to income, payment after
expenses, savings+checking buffer in months of payment, utilisation x DTI, DTI x LTV and a
combined delinquency score; all built from clean fields only. Per-loan stake weights and the
decision rule use LOAN_AMOUNT, LOAN_TERM and MONTHLY_PAYMENT (clean fields).

Conclusion: every variant lands within about +-1 of 121.0 (and the only positive one, +0.1, is
noise); at the fitted public scale (about 0.45) these differences are worth under +-0.5 on the
public score, below its sampling noise (about 1.0). The model's ranking has saturated and the
decision rule is already near optimal for the fitted formula, so these ideas do not justify
another probe. Gains that would need the excluded fields were not tested. rw/experiment_log.jsonl
has a summary record of these runs; OOF predictions are in rw/oof (profit_reg, xgb_w, lr_w,
xgb_fe, lr_fe).

## Seed bagging and retraining (2026-10-29)

Question: since XGBoost training depends on the random seed, can retraining the best model
(clean 57-column ensemble behind cand_clean_rule50) give a higher result? Method: 5-fold OOF
with 4 new seeds for XGB depth 2 and 3 (seeds 11-14; logistic regression is deterministic), same
hyperparameters and folds; per-loan rule at loss 0.5.

| Run | Rule profit ($M, loss 0.5) | AUC |
|---|---|---|
| single seed, ensemble per seed (11 / 12 / 13 / 14) | 120.90 / 120.98 / 120.87 / 120.75 | about 0.7987 |
| original rule50 seed | 120.97 | 0.7987 |
| 4-seed averaged ensemble | 120.9 (best cutoff 120.3; loss 0.4 / 0.6: 134.2 / 107.6) | 0.7986 |

- Seed-to-seed spread of the OOF profit is about 0.2 $M (sd about 0.1), i.e. about +-0.05 on the
  public scale (x0.45). Bagging does not improve on a single seed (120.9 vs 120.97), so retraining
  cannot raise the expected score; the original seed sits at the favourable end of the four.
- Final model refit on all 100K rows with 10 averaged seeds (21-30) per XGB depth plus the
  logistic regression, in two halves of 5 seeds (a first single run hit a SAS session timeout and
  the compute session was reset; saved files were untouched). Predicted-PD correlation with the
  single-seed final model is 0.9996; the per-applicant sd across seeds of the XGB-d2 prediction is
  about 0.005.
- Per-loan rule at loss 0.5 on the scoring table: `cand_clean_rule50_bag.csv` (VFL, rw/submissions;
  not downloaded, not uploaded): 100,000 unique integer IDs, approval 82.42% vs 82.47% for rule50.
  616 applicants (0.62%) differ from rule50: 283 become approved, 333 become declined. Expected
  public-score change: about 0 (+-0.1), well inside noise. Seeds are not to be chosen by public score.
- Logged also in rw/experiment_log.jsonl and rw/oof (bag4, bag_parts_A/B, score_pd_clean_bag10).

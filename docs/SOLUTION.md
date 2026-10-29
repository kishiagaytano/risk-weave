# Solution summary: Risk Weave (SAS Hackathon 2026, Student Track)

## One-page summary

**Task.** For each of 100,000 new auto-loan applications decide approve (1) or do not approve (0). The score
(a "Responsible Profit Score", in $M) rewards profit while the Overview asks for a balance of profitability, risk
management, access to credit, fairness and explainability. The exact formula is not published.

**Approach.**
1. *Estimate default risk* with an equal-weight ensemble of a regularised logistic regression and two shallow
   XGBoost models, trained on 57 "clean" columns (no race/ethnicity, gender, age or marital status; no interest
   rate; no proxy-prone or timing-uncertain fields). Out-of-fold AUC 0.7987, probabilities well calibrated.
2. *Turn risk into a decision* with a per-loan expected-profit rule: approve when
   `(1 - PD) x interest earned > PD x loss`, where interest earned = scheduled payments minus principal and
   loss = 50% of the loan amount. This replaces an arbitrary 0.5 probability cut-off.
3. *Check against the metric* using the public leaderboard as evidence: six public scores fit this profit model to
   within about 1 point (most within 0.5), which is how the loss fraction was chosen.
4. *Stay explainable and fair*: every input is a documented credit attribute, the model is dominated by a
   transparent logistic regression, protected attributes and their proxies were excluded at no measurable cost, and
   group-level outcomes are reported.

**Results.** Best public score **54.429** (`rule50`), hedge `cand_clean_t25` 54.290; cross-validated profit of the
rule is about 0.2% above the best single cutoff, and it beat every single cutoff on 100% of 400 random 60% resamples
of the out-of-fold data (mean margin 0.57-1.1 $M of a 60K-loan subset against cutoffs 0.25-0.28).

**SAS Viya for Learners.** Data access, modelling (SAS Studio Python with scikit-learn and XGBoost), the final fit
and scoring, and a Model Studio baseline all ran inside VFL; see `vfl-usage.md`.

**Deliberately not done.** No use of race/ethnicity, gender, age, marital status, interest rate, proxy-prone or
timing-uncertain fields; no seed picking or model tuning on the public leaderboard; no competition data in this
repository.

---

## Detail

### 1. Data and audit
* Training: 100,000 labelled loans, 13.48% defaulted, 83 columns. Scoring: 100,000 loans, 82 columns (no `DEFAULT`).
* Identifiers are unique, no duplicate rows ignoring the ID, train and scoring schemas match. Seven columns have 4-12%
  missing values with the same rates in scoring (`HOUSEHOLD_INCOME`, `SAVINGS_BALANCE`, `CHECKING_BALANCE`,
  `FINANCIAL_LITERACY_SCORE`, `MEDICAL_DEBT_FLAG`, `BANKING_RELATIONSHIP_YRS`, `BRANCH_DISTANCE`); missingness is not
  informative for default. Train and scoring distributions of the loan fields match (no drift found).
* `metadata.csv` gives only short labels, so decision-time availability of each field cannot be confirmed from it.

### 2. Features
* Excluded from the model by decision: `RACE_ETH`, `GENDER`, `AGE_BAND`, `AGE_D`, `MARITAL_STATUS` (sensitive);
  `INTEREST_RATE` (may encode the bank's own risk pricing); 14 proxy-capable fields (`STATE`, `STATE_TIER`,
  `RURAL_URBAN`, `PRIMARY_LANGUAGE`, `FIRST_GEN_COLLEGE`, `VETERAN`, `COMMUNITY_INVESTMENT_AREA`,
  `PUBLIC_TRANSIT_ACCESS`, `HISTORIC_ACCESS_SCORE`, `WEALTH_GAP_PROXY`, `COST_OF_LIVING_INDEX`, `MEDICAL_DEBT_FLAG`,
  `INSURANCE_COST_TIER`, `DEPENDENTS`); four fields whose recording time is uncertain (`PREVIOUS_APPROVAL_FLAG`,
  `PREVIOUS_DENIAL_FLAG`, `CREDIT_BUILDER_FLAG`, `CREDIT_MONITORING_FLAG`).
* The exclusions are nearly free: adding the sensitive columns back raised XGBoost AUC from 0.7977 to 0.7982; removing
  the proxies and timing fields changed it by at most 0.0002; removing the interest rate cost about 0.001.
* Preprocessing: median imputation with missing indicators for numerics; one-hot for categoricals (levels with fewer
  than 20 rows pooled); standardisation for the logistic regression.

### 3. Models and validation
* Members: L2 logistic regression (C = 0.1); XGBoost depth 2 (800 trees, learning rate 0.05); XGBoost depth 3
  (500 trees, learning rate 0.04, min child weight 20, lambda 10). Equal-weight average of probabilities.
* 5-fold stratified cross-validation, seed 20261028, out-of-fold predictions.

| Model (clean features, out-of-fold) | AUC | Note |
|---|---|---|
| Logistic regression | about 0.797 | transparent baseline |
| XGBoost depth 2 / depth 3 | about 0.798 / 0.7975 | shallow trees match or beat deeper ones |
| **Equal-weight ensemble** | **0.7987** | final model |
| Logistic regression with splines | 0.799 | same as shallow XGBoost: signal is smooth and additive |
| Model Studio gradient boosting / stepwise logistic (reference) | KS 0.369 / 0.362 on a 10K test split | not directly comparable (Youden KS, untuned defaults) |

* Extra ideas tested and rejected, each within about +-1 of the rule's profit of 121.0 $M (out-of-fold, loss 0.5):
  stake-weighted training, profit-aware XGBoost (worse by 1.1), stacking (identical), engineered ratio features
  (no gain), collateral-aware loss (no robust gain), seed bagging (spread +-0.1 $M). See `experiment-log.md`.

### 4. From probability to decision
* A single probability cutoff ignores that loans differ in size and interest. The per-loan rule approves when
  expected profit is positive. Under the fitted formula it adds about 0.2% to the best single cutoff and, more
  importantly, makes the decision logic explicit and defensible: it is the textbook expected-value rule.
* The metric is unpublished, so profit was evaluated over eight documented scenarios first; the best cutoff ranged
  from 0.04 to 0.38 depending on the assumption. The public scores then pinned it down: public score divided by
  out-of-fold profit was 0.4429 and 0.4432 at cutoffs 0.07 and 0.12 for a loss of 50% of the loan (40% or 70% did not
  match the ratio), and later probes (0.20, 0.25, 0.28 and the rule file) were predicted within about 0.8 (errors +0.8, +0.8, -0.1 to -0.6 and about 0).

### 5. Results

| Submission | Approved | Public score | Cross-validated profit (loss 0.5, $M of 100K loans) |
|---|---|---|---|
| per-loan rule (`rule50`) | 82.47% | **54.429** | 121.0 |
| rule, 10-seed average | 82.42% | 54.370 | 120.9 (4-seed out-of-fold average) |
| cutoff 0.25 | 84.43% | 54.290 | about 120.8 |
| cutoff 0.20 | 78.59% | 53.935 | 119.8 |
| cutoff 0.28 | 87.03% | 53.924 | about 120 |
| cutoff 0.12 | 62.55% | 47.159 | 106.4 |
| cutoff 0.07 | 43.98% | 34.812 | 78.6 |

### 6. Why these final two submissions
* **`cand_clean_rule50`** is the highest public score and has the highest cross-validated profit; it is the principled
  expected-profit policy.
* **`cand_clean_t25`** is the best single-cutoff file (54.290) and a hedge: if the hidden metric penalises large or
  risky loans differently from the fitted formula, a plain risk cutoff fails in a different way from the rule.
* The 10-seed bagged rule (54.370) is a lower-variance twin of `rule50`; the 0.06 gap to `rule50` is seed noise (only
  0.62% of decisions differ), so it is a valid substitute but was not preferred because it is not better.
* Final selection on Kaggle is made by the participant.

### 7. Responsible-lending evidence
Group outcomes, excluded variables, proxy analysis, coefficients and limitations are in
`fairness-and-explainability.md`. In short: default rate among approved loans is 6.2-10.2% for every demographic
level, approval rates differ by group because underlying default rates differ (not because of protected inputs), and
the lowest approval ratios (education 0.77, state tier 0.83, employment 0.83) are disclosed rather than corrected.

### 8. Limitations
* The profit formula is inferred (fit to the public scores), not known; it reproduces them to within about 1 point.
* No time variable, so no out-of-time test; public/private rank shifts are expected for differences under about 1 point.
* Some inputs (banking-relationship flags such as auto-pay, direct deposit) are strong predictors whose decision-time
  availability cannot be confirmed from the metadata.
* VFL package versions were recorded on 2026-10-29 (`vfl-environment.md`), after the modelling runs; no upgrade was observed, but earlier runs cannot be proven to have used the identical image.

# Model card: Risk Weave approval ensemble (candidate v1)

> **Status (2026-10-29):** the final model is the `clean` 57-column ensemble with the per-loan expected-profit rule
> (`cand_clean_rule50`, public 54.429). Sections below were written for the earlier `no_rate` candidate and the
> cutoff probes and are kept for history; the up-to-date summary is `SOLUTION.md`, the group outcomes are in
> `fairness-and-explainability.md`, and all numbers agree with `experiment-log.md`.


## Purpose and decision
Decide, for each applicant in `ILINK_CREDITRISK_SCORING_PUBLIC`, whether to
approve an iLink Capital Bank auto loan (`APPROVED` 1/0). The model estimates the
probability of default (PD); the policy approves when PD is below a cutoff.

## Data
- Training: `CREDITr.ILINK_CREDITRISK_TRAINING`, 100,000 labelled loans, 13.48%
  defaults. Scoring: `CREDITr.ILINK_CREDITRISK_SCORING_PUBLIC`, 100,000 loans.
  Both stay inside SAS Viya for Learners; this repository holds only code and
  aggregate results.
- Train and scoring distributions of key loan fields match; mean predicted PD on
  scoring is 0.134 vs 0.135 observed training default rate.

## Features
- All columns except `LOAN_ID`, `DEFAULT`, five sensitive columns (`RACE_ETH`,
  `GENDER`, `AGE_BAND`, `AGE_D`, `MARITAL_STATUS`) and `INTEREST_RATE`.
- Numerics: median imputation plus missing indicators. Categoricals: one-hot
  (levels under 20 rows pooled). Logistic regression also standardises numerics.
- Excluded variables: the sensitive five are excluded by decision; they add only
  about 0.0005 AUC (XGBoost 0.7982 with vs 0.7977 without). `INTEREST_RATE` is
  excluded because it may encode the bank's own risk pricing and adds only about
  0.001 AUC. Other proxy-capable fields (for example `STATE`, `STATE_TIER`,
  `WEALTH_GAP_PROXY`, `HISTORIC_ACCESS_SCORE`, `MEDICAL_DEBT_FLAG`) remain in the
  model and are a known limitation; a `no_proxy` feature set exists for
  sensitivity checks but has not been run yet.
- Decision-time availability is not documented in `metadata.csv`; the
  `PREVIOUS_*` and relationship flags were kept but are untested for timing
  leakage (a `no_timing` set exists, not yet run).

## Recommended update (feature set `clean`)
Sensitivity runs (experiment log) show that removing the 14 proxy-capable fields
and the 4 timing-uncertain flags costs at most 0.0002 AUC. The recommended final
model therefore uses the `clean` feature set (57 columns; also excludes the five
sensitive columns and `INTEREST_RATE`). The `no_rate` description below remains
valid for the v1 candidates.

## Model
Equal-weight average of three models trained on all labelled rows: L2 logistic
regression (C=0.1); XGBoost depth 2 (800 trees, learning rate 0.05); XGBoost depth
3 (500 trees, learning rate 0.04, min child weight 20, lambda 10). Seed 20261028.
Libraries available in VFL only (scikit-learn, XGBoost).

## Validation
5-fold stratified CV, out-of-fold predictions. Best single models AUC about
0.799; ensemble about 0.800 (PR-AUC about 0.427, logloss about 0.321). Raw
probabilities are well calibrated (ECE about 0.001-0.002). Fold AUC standard
deviation about 0.002. Details: `docs/experiment-log.md`.

## Policy and threshold selection
The official Responsible Profit formula is unpublished. Profit was evaluated over
eight documented gain/loss scenarios (see experiment log). The best cutoff
ranges from 0.04 to 0.38 depending on the scenario. Candidates: 0.07 (defensive,
positive profit in every scenario), 0.12 (mid-point), 0.20 (aggressive). The
choice is not made from the public leaderboard alone.

## Fairness checks (OOF, cutoff 0.07)
Sensitive attributes are not model inputs. Approval rates: White 0.46, Asian
0.46, Hispanic 0.42, Black 0.39; default rate among approved is 3.2-3.9% for all
race groups, 3.4-4.4% by gender. State tier L approval 0.31 vs H 0.56. The
gaps reflect default-rate differences in the data; no correction has been applied.
Disparity versus the four-fifths rule: Black/White ratio about 0.84.

## Limitations
- Profit model is an assumption; real payoffs may change the best cutoff.
- No time dimension in the data, so no out-of-time validation.
- Proxy variables and possibly post-decision flags may remain in the feature set.
- Signal ceiling: AUC about 0.80; more model complexity did not help.

## Reproducibility
Code in `src/risk_weave`; packaged for VFL by `tools/pack_for_vfl.py` (an
encoding of the same code); executed with Python in SAS Studio. Experiment
records are in `~/rw/experiment_log.jsonl` inside VFL; summaries are in
`docs/experiment-log.md`.

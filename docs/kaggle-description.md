# Kaggle submission descriptions

Short text for each of the two final entries (no personal data, no competition data, no loan IDs). Numbers are on the
scoring file; public scores are as reported by the participant.

## Entry 1: `cand_clean_fit70m18` (public 54.463, approves 83.51%)

Auto-loan approval by per-loan expected profit. Default probability (PD) comes from an equal-weight ensemble of
regularised logistic regression and two shallow XGBoost models on 57 credit attributes (5-fold out-of-fold AUC about
0.80, well calibrated). A loan is approved when (1 - PD) x total interest > PD x 0.7 x (loan - 18 monthly payments). The
competition does not publish its profit formula, so this loss shape was fitted to public-score behaviour and checked for
robustness (leave-one-out). Race, gender, age and marital status are excluded from the model and analysed separately for
fairness. Built in SAS Viya for Learners; code, seeds and checksums are in the repository
(github.com/kishiagaytano/risk-weave, MIT). Differs from my other entry on 1.6% of loans.

## Entry 2: `cand_clean_rule50` (public 54.429, approves 82.47%)

Same default-probability ensemble (logistic regression plus XGBoost depth 2 and 3, 57 credit attributes, 5-fold
out-of-fold AUC about 0.80, well calibrated), with the simplest loss assumption: approve when (1 - PD) x total interest >
PD x 0.5 x loan amount. It is a deliberate hedge against my other entry, whose loss formula was fitted to public scores.
Race, gender, age and marital status are excluded from the model and analysed separately for fairness. Built in SAS Viya
for Learners; code, seeds and checksums are in the repository (github.com/kishiagaytano/risk-weave, MIT). Differs from
my other entry on 1.6% of loans.

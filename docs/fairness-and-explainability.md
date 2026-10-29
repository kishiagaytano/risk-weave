# Fairness and explainability report

All numbers are aggregates from out-of-fold predictions of the final policy (clean ensemble + per-loan expected-profit
rule, loss fraction 0.5) on the 100,000 training loans: overall approval 82.3% (82.5% on the scoring table), default
rate 8.2% among approved loans versus 38.0% among declined loans (observed overall 13.5%). Sensitive attributes were
**not** model inputs; they are used here only to audit outcomes.

## 1. Group outcomes of the final policy

Approval = share approved; default | approved = observed default rate among the approved; default (all) = observed
default rate of the whole group.

| Attribute | Level | n | Approval | Default among approved | Default (all) |
|---|---|---|---|---|---|
| Race / ethnicity | Asian | 11,364 | 83.8% | 7.9% | 12.8% |
| | Black | 21,591 | 79.3% | 8.7% | 15.0% |
| | Hispanic | 15,697 | 81.5% | 8.8% | 14.2% |
| | Other | 7,654 | 80.9% | 8.4% | 14.2% |
| | White | 43,694 | 83.9% | 7.8% | 12.5% |
| Gender | Female | 48,997 | 82.3% | 8.2% | 13.4% |
| | Male | 49,457 | 82.3% | 8.2% | 13.5% |
| | Nonbinary | 1,546 | 82.5% | 8.9% | 14.1% |
| Age band | 18-29 | 16,756 | 78.8% | 8.9% | 15.0% |
| | 30-44 | 40,729 | 82.3% | 8.2% | 13.5% |
| | 45-59 | 33,529 | 83.2% | 7.9% | 12.9% |
| | 60+ | 8,986 | 85.3% | 8.0% | 12.7% |
| Marital status | Married | 44,605 | 82.5% | 8.1% | 13.2% |
| | Single | 55,395 | 82.1% | 8.3% | 13.7% |
| State tier | H | 26,050 | 89.4% | 6.9% | 9.9% |
| | M | 45,084 | 83.2% | 8.0% | 13.0% |
| | L | 28,866 | 74.4% | 10.0% | 17.5% |
| Employment | Full-time | 55,066 | 86.0% | 7.6% | 11.7% |
| | Part-time | 17,503 | 78.5% | 8.9% | 15.3% |
| | Retired | 1,870 | 84.0% | 7.9% | 13.4% |
| | Self-employed | 13,167 | 81.9% | 8.3% | 13.7% |
| | Unemployed | 12,394 | 71.2% | 10.1% | 18.6% |
| Education | Advanced degree | 7,974 | 92.1% | 6.2% | 8.6% |
| | Bachelor's | 22,250 | 87.8% | 7.5% | 10.9% |
| | Some college | 33,794 | 83.4% | 8.0% | 12.9% |
| | High school | 24,110 | 78.2% | 9.2% | 15.6% |
| | Less than high school | 11,872 | 70.5% | 10.2% | 18.9% |
| Rural / urban | Rural | 23,770 | 81.3% | 8.4% | 13.9% |
| | Suburban | 49,407 | 82.3% | 8.1% | 13.3% |
| | Urban | 26,823 | 83.0% | 8.2% | 13.4% |

**Reading.**
* *Equal treatment of equal risk.* Within every attribute the default rate among approved loans differs by at most
  about 4 points (6.2% to 10.2% overall; 7.8% to 8.8% across all five race groups; 8.2% to 8.9% across gender), and
  the policy declines the loans that default most (38.0% default among declined). Predicted and observed default rates
  agree across probability bins (for example 0.223 vs 0.235 in the 0.20-0.25 bin), so risk estimates are not biased
  against a group in aggregate.
* *Approval ratios* (lower group / higher group): race Black/White 0.945, age 18-29 / 60+ 0.924, gender 1.00, state tier
  L/H 0.832, unemployed / full-time 0.828, education less than high school / advanced degree 0.765.
  Only education falls below the common four-fifths guideline. Differences track genuine default differences
  (default rate 18.9% for less than high school vs 8.6% for advanced degree), and education, employment and state tier
  are used here only as far as they carry credit signal; none is a protected class in this dataset, but the gaps are
  disclosed and should be reviewed by credit-policy owners, not treated as settled.
* *No correction was applied.* The task rewards balancing profit and access; adjusting thresholds by group would use
  protected attributes at decision time, which the solution deliberately avoids.

## 2. Variables excluded and why

| Group | Fields | Reason | Cost of excluding |
|---|---|---|---|
| Sensitive | `RACE_ETH`, `GENDER`, `AGE_BAND`, `AGE_D`, `MARITAL_STATUS` | Protected-class attributes must not drive credit decisions | XGBoost AUC 0.7982 with them vs 0.7977 without (+0.0005) |
| Pricing | `INTEREST_RATE` | May encode the bank's own risk assessment (circularity) and was not needed | about 0.001 AUC |
| Proxy-capable (14) | `STATE`, `STATE_TIER`, `RURAL_URBAN`, `PRIMARY_LANGUAGE`, `FIRST_GEN_COLLEGE`, `VETERAN`, `COMMUNITY_INVESTMENT_AREA`, `PUBLIC_TRANSIT_ACCESS`, `HISTORIC_ACCESS_SCORE`, `WEALTH_GAP_PROXY`, `COST_OF_LIVING_INDEX`, `MEDICAL_DEBT_FLAG`, `INSURANCE_COST_TIER`, `DEPENDENTS` | Geography and background fields can stand in for protected attributes | at most 0.0002 AUC |
| Timing-uncertain (4) | `PREVIOUS_APPROVAL_FLAG`, `PREVIOUS_DENIAL_FLAG`, `CREDIT_BUILDER_FLAG`, `CREDIT_MONITORING_FLAG` | Their recording time relative to the decision is not documented | no loss (+0.0002) |

Excluding all of these removed no measurable predictive power, which is why the 57-column set was chosen as final.

## 3. Explainability

* **Structure.** One third of the ensemble is a logistic regression, whose standardised coefficients are directly
  readable; the other two thirds are depth-2 and depth-3 trees, which are deliberately shallow (low-order
  interactions only). Logistic regression with splines matched the trees' accuracy (AUC 0.799), indicating that the
  risk signal is smooth and mostly additive.
* **Largest logistic-regression effects** (standardised coefficients; positive raises default risk):

| Input | Coefficient |
|---|---|
| `REVOLVING_UTILIZATION` | +0.34 |
| `DOWN_PAYMENT_PCT` | -0.28 |
| `RECENT_INQUIRIES_12M` | +0.27 |
| `MONTHLY_PAYMENT` | +0.27 |
| `AUTO_PAY_FLAG` = Yes | -0.26 |
| `DEBT_TO_INCOME` | +0.26 |
| `LOAN_TERM` | +0.24 |
| `TOTAL_CREDIT_LIMIT` | +0.23 |
| `DIRECT_DEPOSIT_FLAG` = Yes | -0.22 |
| `LOAN_AMOUNT` | -0.22 |
| `NEW_USED_FLAG` = Used | -0.20 |

  (`LOAN_AMOUNT` and `MONTHLY_PAYMENT` are correlated, so their opposite signs partly offset; read them together.)
* **Corroboration.** The Model Studio gradient-boosting variable importances rank revolving utilisation,
  debt-to-income, missed payments and down payment highest, consistent with the regression and with credit-risk
  practice.
* **Decision rule.** Every approval has a one-line reason: expected interest income exceeds expected loss given the
  applicant's predicted default probability and loan terms. Both sides of the inequality are in dollars and can be shown
  to a reviewer.
* SHAP and permutation importance were not computed: SHAP is not installed in VFL, and the coefficient table plus
  the Model Studio importances were judged sufficient for a model of this size.

## 4. Limitations
* The profit rule's loss fraction (50% of the loan) is inferred from public leaderboard scores, not given.
* Banking-relationship flags (auto-pay, direct deposit, emergency fund, mobile banking) are strong predictors, but their
  decision-time availability cannot be confirmed from the metadata; they were kept because they are ordinary account
  attributes, and this should be reviewed.
* Education, employment and geography effects are correlational; they may partly reflect historical access to credit.
* No out-of-time validation is possible (no date field), and fairness was measured on the same data the model was
  trained on (out-of-fold, so not in-sample, but from the same population).
* Group labels are the dataset's own categories; intersectional effects (for example race x state tier) were not
  analysed.

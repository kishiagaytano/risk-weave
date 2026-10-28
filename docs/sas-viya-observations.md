# SAS Viya data exploration — observations

Read-only exploration of the full VFL tables on 2026-10-28. Commands are in
[`sas-viya-commands.sas`](sas-viya-commands.sas). Only aggregate statistics are
recorded here; no row-level data.

## Competition facts gathered from Kaggle (Overview, Rules, Data tabs)

- The exact scoring metric ("Responsible Profit Score", shown in $M) is
  **not published**; the page says the methodology is intentionally withheld.
  It rewards profit but also credit access, fairness and explainability.
- Submission: `LOAN_ID,APPROVED` (1/0), one row per scoring `LOAN_ID`.
- Limits: 5 submissions/day, up to 2 final submissions; individual entries only.
- Leaderboard closes 2026-10-30 12:00 ET. Public/private split is not stated
  on the pages read (a 40%/60% split is reported elsewhere but unconfirmed).
- Python is not forbidden; prize winners must demonstrate use of SAS Viya for
  Learners and provide reproducible documentation/code.
- Kaggle files are samples; the full data is in VFL. Data must not be shared
  or redistributed outside the competition.
- `metadata.csv` (not yet reviewed here) holds the column descriptions.

## Where the data is (SAS Viya for Learners)

Apps menu > Manage Data > Sources > In-memory data; caslib `CREDITr`:

| Table | Rows | Columns |
|---|---|---|
| `ILINK_CREDITRISK_TRAINING` | 100,000 | 83 |
| `ILINK_CREDITRISK_SCORING_PUBLIC` | 100,000 | 82 |

The scoring table name ends in `_PUBLIC`; whether it is the same set used for
the public leaderboard is unconfirmed. `ILINKMORTGAGE_SCORING` (ACADEMIC, 2.5K
rows) also exists and looks unrelated.

## Schema (training, 83 columns)

`LOAN_ID`, demographics (`AGE_BAND`, `GENDER`, `RACE_ETH`, `STATE`,
`STATE_TIER`, `RURAL_URBAN`, `EDUCATION`, `PRIMARY_LANGUAGE`, `MARITAL_STATUS`,
`AGE_D`, `VETERAN`, `FIRST_GEN_COLLEGE`, `DEPENDENTS`), employment/income/assets
(`EMPLOYMENT_STATUS`, `EMPLOYER_TIER`, `INDUSTRY`, `OCCUPATION_SKILL_LEVEL`,
`HOMEOWNER`, `YEARS_EMPLOYED`, `INCOME_VOLATILITY`, `HOUSEHOLD_INCOME`,
`REPORTED_INCOME`, `MONTHLY_EXPENSES`, `SAVINGS_BALANCE`, `CHECKING_BALANCE`,
`DEBT_TO_INCOME`, `FINANCIAL_LITERACY_SCORE`), credit history (`YEARS_CREDIT_HISTORY`
through `BANKRUPTCY_FLAG`, columns 29-45), vehicle and loan terms
(`VEHICLE_TYPE` through `PAYMENT_TO_INCOME`, columns 46-59), context/access
fields (`COMMUNITY_INVESTMENT_AREA`, `PUBLIC_TRANSIT_ACCESS`,
`INSURANCE_COST_TIER`, `HISTORIC_ACCESS_SCORE`, `WEALTH_GAP_PROXY`,
`COST_OF_LIVING_INDEX`, `MEDICAL_DEBT_FLAG`), banking-relationship flags
(columns 67-82, e.g. `PREVIOUS_DENIAL_FLAG`, `SUBPRIME_HISTORY_FLAG`), and the
target `DEFAULT` (column 83). The scoring table has the same columns minus
`DEFAULT`.

## Target balance

`DEFAULT`: 86,521 repaid (86.52%), 13,479 defaulted (13.48%).

## Missing values

| Column | Training missing | Scoring missing |
|---|---|---|
| `HOUSEHOLD_INCOME` | 4,072 | 3,955 |
| `SAVINGS_BALANCE` | 6,421 | 6,480 |
| `CHECKING_BALANCE` | 4,504 | 4,528 |
| `FINANCIAL_LITERACY_SCORE` | 11,956 | 12,039 |
| `MEDICAL_DEBT_FLAG` | 5,122 | 5,073 |
| `BANKING_RELATIONSHIP_YRS` | 6,520 | not checked |
| `BRANCH_DISTANCE` | 6,111 | 5,932 |

All other numeric columns checked have no missing values. Character columns
showed no missing level in the frequency output. DEFAULT rate differs little by
missingness (largest gaps: `CHECKING_BALANCE` missing 15.65% vs 13.38%;
`BANKING_RELATIONSHIP_YRS` missing 14.62% vs 13.40%).

## Train vs scoring

Key numeric ranges and means for `LOAN_AMOUNT`, `INTEREST_RATE`, `LOAN_TERM`
and `MONTHLY_PAYMENT` are nearly identical (e.g. mean loan about $20.4K,
`LOAN_TERM` 48-84, `INTEREST_RATE` 0.029-0.086). No obvious drift. `LOAN_ID`
values are not sequential (about 1 to 499,999).

## DEFAULT rate by segment (training; overall 13.48%)

- `EDUCATION`: Advanced Degree 8.57%, Bachelor's 10.90%, Some College 12.93%,
  High School 15.57%, Less than HS 18.94%.
- `EMPLOYMENT_STATUS`: Full-time 11.68%, Part-time 15.31%, Retired 13.42%,
  Self-employed 13.71%, Unemployed 18.64% (12.4% of rows).
- `HOMEOWNER`: Owner 10.11%, Renter 16.12%.
- `STATE_TIER`: H 9.93%, M 12.97%, L 17.47%.
- `DEALER_NETWORK_TIER`: High 9.72%, Medium 13.20%, Low 17.33%.
- `NEW_USED_FLAG`: New 11.88%, Used 14.35%.
- `PREVIOUS_DENIAL_FLAG`: No 12.89%, Yes 15.79%. `PREVIOUS_APPROVAL_FLAG`: No
  15.15%, Yes 11.49%. `SUBPRIME_HISTORY_FLAG`: No 12.77%, Yes 16.96%.
- `VEHICLE_TYPE`: 13.15% (Sedan) to 15.42% (Luxury).
- `RURAL_URBAN`, `MARITAL_STATUS`, `GENDER`: within about 1 percentage point.
- Protected-attribute gaps: `RACE_ETH` White 12.50%, Asian 12.79%, Hispanic
  14.23%, Other 14.24%, Black 15.01%; `AGE_BAND` 18-29 14.97% down to 60+
  12.68%.

## DEFAULT rate by decile (10,000 rows each)

| Decile | `INTEREST_RATE` | `DEBT_TO_INCOME` | `LOAN_TO_VALUE` |
|---|---|---|---|
| 0 (lowest) | 2.21% | 2.29% | 9.23% |
| 1 | 3.89% | 4.41% | 11.49% |
| 2 | 6.10% | 6.32% | 9.77% |
| 3 | 7.53% | 7.25% | 8.69% |
| 4 | 9.27% | 9.91% | 8.99% |
| 5 | 11.87% | 11.69% | 10.57% |
| 6 | 14.22% | 14.17% | 11.13% |
| 7 | 18.64% | 18.19% | 13.85% |
| 8 | 23.92% | 23.28% | 21.55% |
| 9 (highest) | 37.14% | 37.28% | 29.52% |

Spearman correlation with `DEFAULT`: `INTEREST_RATE` 0.278, `DEBT_TO_INCOME`
0.272, `LOAN_TO_VALUE` 0.145.

## Leakage and fairness notes (judgment, not proof)

- `INTEREST_RATE` tracks `DEFAULT` almost exactly like `DEBT_TO_INCOME`, which
  suggests risk-based pricing or a shared latent risk. It is an application-time
  field, but may duplicate the bank's own risk score; compare models with and
  without it.
- `PREVIOUS_*` flags show modest effects; their recording time is unknown.
- Segment effects are univariate and not controlled for each other.
- `RACE_ETH`, `AGE_BAND`, `GENDER`, `STATE_TIER`, `MARITAL_STATUS` and similar
  fields show default-rate gaps or are sensitive proxies. Decide deliberately
  whether to use them as model inputs.

## Open items

- Official scoring formula unknown; working assumption (mine, unverified): an
  approved good loan earns roughly its interest, a default loses roughly the
  loan amount.
- Review `metadata.csv` for column meanings and the timing of
  `PREVIOUS_*`/relationship fields.
- Check `BANKING_RELATIONSHIP_YRS` missingness and character-column placeholder
  values in the scoring table.

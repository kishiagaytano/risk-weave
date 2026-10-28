# Risk Weave — project context

## Project identity

**Repository name:** `risk-weave`

**Challenge:** SAS Hackathon 2026 Student Track

**Business setting:** iLink Capital Bank auto-loan credit approval

Risk Weave is a credit-risk modeling and decisioning project. Its purpose is to
help determine which future auto-loan applicants should be approved, balancing
the opportunity to lend with the risk of borrower default.

## Competition objective

The historical training data contains applicant characteristics, financial
indicators, credit-history information, loan attributes, and the target
`DEFAULT`:

- `DEFAULT = 0`: the borrower repaid successfully;
- `DEFAULT = 1`: the borrower defaulted.

The scoring data contains the same predictor fields without the observed
outcome. The final competition decision is an approval flag, not a default
probability:

```text
LOAN_ID,APPROVED
100001,1
100002,0
```

Each scoring application must appear exactly once.

## Known competition files

- `ilink_creditrisk_training_sample.csv` — sample historical applications with
  `DEFAULT` for model development;
- `ilink_creditrisk_scoring_sample.csv` — sample future applications without
  `DEFAULT`;
- `metadata.csv` — supplemental variable descriptions;
- `sample_submission.csv` — required submission shape and column names.

The Kaggle files are samples for learning the workflow. Complete modeling,
decisioning, and scoring are expected to use the larger datasets in SAS Viya
for Learners (VFL) when available.

## Modeling direction

The project should generally follow this sequence:

1. profile the data and reconcile it with `metadata.csv`;
2. check leakage, missingness, class balance, outliers, duplicate IDs, and
   train/scoring schema alignment;
3. establish a reproducible baseline for probability of default;
4. compare suitable statistical, machine-learning, or hybrid approaches;
5. convert predicted risk into an explicit approval policy;
6. validate the policy and generate a schema-correct submission;
7. record assumptions, experiment settings, and results for iteration.

The approval threshold should be selected from validation evidence and the
competition scoring behavior, not inherited automatically from a classifier's
default cutoff.

## Working boundaries

Competition rules, the VFL materials, and the current metadata are the
authoritative sources for permitted data use and scoring. Keep credentials,
activation codes, personal contact details, and restricted competition data out
of version control. Sample data may be committed only if its license and the
competition rules allow it.

## Name rationale

“Risk Weave” is intentionally more specific and uncommon than a generic
`credit-risk-model` name: it reflects weaving heterogeneous applicant and loan
signals into an explainable approval strategy. It also leaves room for the
project to grow from a single model into a repeatable risk-to-decision system.


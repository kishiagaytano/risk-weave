# Risk Weave

Credit-risk modeling and approval decisioning for the [SAS Hackathon 2026
Student Track](https://www.kaggle.com/competitions/sas-hackathon-2026/overview)
auto-loan challenge for iLink Capital Bank.

Risk Weave combines applicant, financial, credit-history, and loan signals to
estimate default risk and turn those estimates into approval decisions. The
competition output is one `APPROVED` flag per `LOAN_ID`, rather than a default
probability alone.

## Project map

- `PROJECT_CONTEXT.md` — competition context, data files, modeling direction,
  and decision-policy notes;
- `AGENTS.md` — durable instructions for future project work;
- `instruction-decisions.md` — assumptions, source decisions, and excluded
  sensitive or time-sensitive details;
- sample CSV files — local examples of the training, scoring, metadata, and
  submission formats.

## Intended workflow

1. Understand the data and reconcile it with `metadata.csv`.
2. Check leakage, missingness, class balance, and schema alignment.
3. Build reproducible default-risk models.
4. Evaluate an explicit risk-to-approval policy.
5. Generate and validate a schema-correct submission.

Use the Kaggle overview and its linked/subsequent tabs for the latest
competition rules, files, scoring details, and updates. Full SAS Viya for
Learners datasets are not included in this repository unless the competition
rules permit them.

## Status

The repository foundation and project context are in place. Modeling,
validation, and submission-generation work will be added iteratively.


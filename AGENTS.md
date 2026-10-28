# Risk Weave project instructions

## Identity and purpose

Risk Weave is a SAS Hackathon 2026 Student Track project for iLink Capital
Bank's auto-loan credit-approval challenge. The project must turn historical
loan applications into defensible approval decisions for future applicants.

The primary modeling target is `DEFAULT` in the training data. The required
competition output is not a probability: it is one `APPROVED` decision per
`LOAN_ID` in the scoring data, using `1` for approve and `0` for do not approve.

## Durable working rules

- Treat `metadata.csv` as the data dictionary and confirm column meanings before
  building features.
- Keep training, validation, and scoring workflows separate. Never use
  `DEFAULT` or any outcome-derived information when generating scoring features.
- Model probability of default and make the approval policy explicit. Do not
  assume a 0.5 cutoff is optimal; evaluate thresholds and business trade-offs.
- Check class balance, missingness, unusual values, duplicate identifiers, and
  train/scoring schema differences before fitting models.
- Prefer reproducible experiments: record dataset version, feature set, random
  seed, model configuration, validation method, and decision threshold.
- Keep exploratory analysis, preprocessing, model evaluation, decision policy,
  and submission generation separable so each can be audited.
- Do not commit credentials, portal activation codes, private emails, or full
  VFL datasets unless competition rules explicitly permit them.
- Use the competition rules and VFL materials as authoritative when they differ
  from sample files or early notes.

## Expected project outputs

- documented data understanding and quality checks;
- reproducible default-risk models and validation results;
- an approval strategy that maps risk estimates to `APPROVED` decisions;
- a submission file with exactly one row per scoring `LOAN_ID` and columns
  `LOAN_ID,APPROVED`.

## Collaboration and version history

Use focused Conventional Commit messages. Review the diff and validation result
before committing. Push changes only when the user asks for that update or it is
explicitly part of the current task.


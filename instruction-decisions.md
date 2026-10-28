# Instruction decisions

## Sources consulted

- User-provided SAS Hackathon email and competition page text.
- User-provided repository URL: `kishiagaytano/sas-hackathon`.
- Empty local repository cloned to `C:\dev\sas-hackathon`.

## Confirmed decisions

- The local project directory is `C:\dev\sas-hackathon`.
- The repository is being renamed to `risk-weave` at the user's request.
- The project context centers on approval decisions for iLink Capital Bank's
  auto-loan credit-risk competition.
- `DEFAULT` is the historical training outcome; `APPROVED` is the submitted
  decision for scoring applications.

## Assumptions to validate

- The competition metric may reward a decision policy differently from a pure
  probability-ranking metric; threshold selection should therefore be tested
  against the official scoring behavior once the full materials are available.
- The sample files are representative of the workflow but not necessarily of
  the full VFL data's scale, missingness, or distribution.
- The repository can contain project documentation and code, but raw full-size
  VFL data should remain local unless the rules explicitly permit redistribution.

## Deliberately excluded

- The activation code, private contact information, and meeting links from the
  email were excluded from durable project instructions.
- The leaderboard close and winner-announcement dates were treated as
  time-sensitive planning notes rather than permanent repository rules.
- No model, feature, threshold, metric, or fairness claim was promoted to a
  requirement before inspecting the actual datasets and official scoring rules.


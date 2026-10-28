# Competition rules and evaluation (as read 2026-10-28)

Source: Kaggle "SAS Hackathon 2026 | Student Track" Overview, Rules and Data
tabs, read in a browser. Quotes are exact; everything else is summary.

## Confirmed from the pages

- **Scoring:** a "Responsible Profit Score", shown on the leaderboard in
  millions of dollars. Quote: "The exact scoring methodology is intentionally
  withheld to encourage robust and thoughtful lending strategies rather than
  over-optimization to a known metric."
- No per-loan profit or loss amount, no approve/decline payoff and no fairness
  penalty are published. The page says a highly profitable strategy is not
  automatically best if it creates unnecessary barriers to credit access or
  relies on hard-to-defend logic, and approving more applicants is not
  automatically better.
- **Submission:** `LOAN_ID,APPROVED` with a header; `1` = approved, `0` = not
  approved; every scoring application exactly once. Decisions, not
  probabilities.
- **Limits:** 5 submissions per day; up to 2 final submissions selected for
  judging. Individual competition, no teams.
- **Dates:** runs Oct 1 - Oct 30, 2026; leaderboard closes Oct 30, 2026 at
  12:00 ET.
- **Tools:** Python is neither mentioned nor forbidden. Prize winners must
  demonstrate how SAS Viya for Learners (VFL) was used and provide reproducible
  code and documentation.
- **Data:** Kaggle files are samples. Full data is in VFL. Data may only be
  used for this competition and may not be shared or redistributed.
- **Winners:** decided solely by the Private Leaderboard; the public board is
  "a representative sample of the test data".

## Not confirmed

- The 40% public / 60% private split. It was relayed, not found on any page
  read.
- Per-column descriptions (`metadata.csv` not downloaded), the Leaderboard and
  Discussion tabs, and the Learning Portal game guide.

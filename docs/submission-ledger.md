# Submission ledger

Records every candidate file and, once uploaded, its leaderboard result. No file
has been uploaded to Kaggle yet. Candidate files stay in the VFL home folder and
are never committed.

| ID | Model | Feature set | PD cutoff | Approval rate (scoring) | CV evidence | Public LB ($M) | Status |
|---|---|---|---|---|---|---|---|
| cand_t07 | LR + XGB d2 + XGB d3 (mean) | no_rate (excl. 5 sensitive + INTEREST_RATE) | 0.07 | about 44% | OOF AUC 0.798, approval 43.8% on OOF, profit positive in all 8 scenarios | not uploaded | candidate |
| cand_t12 | same | same | 0.12 | about 63% | same model; scenario table in experiment-log.md | not uploaded | candidate |
| cand_t20 | same | same | 0.20 | about 79% | same model; aggressive | not uploaded | candidate (not planned for upload) |

Rules: 5 submissions per day; up to 2 final submissions. A cutoff is not chosen
from the public leaderboard alone: leaderboard results are used only as extra
evidence about the hidden profit formula, alongside the cross-validated
scenario table. Final/private submission selection needs Kish's explicit approval.

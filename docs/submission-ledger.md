# Submission ledger

Records every candidate file and, once uploaded, its leaderboard result. No file
has been uploaded to Kaggle yet. Candidate files stay in the VFL home folder and
are never committed.

| ID | Model | Feature set | PD cutoff | Approval rate (scoring) | CV evidence | Public LB ($M) | Status |
|---|---|---|---|---|---|---|---|
| cand_t07 | LR + XGB d2 + XGB d3 (mean) | no_rate (excl. 5 sensitive + INTEREST_RATE) | 0.07 | about 44% | OOF AUC 0.798, approval 43.8% on OOF, profit positive in all 8 scenarios | not uploaded | candidate |
| cand_t12 | same | same | 0.12 | about 63% | same model; scenario table in experiment-log.md | not uploaded | candidate |
| cand_clean_t07 | LR + XGB d2 + XGB d3 (mean) | clean (excl. 5 sensitive, INTEREST_RATE, 14 proxy-capable and 4 timing-uncertain fields; 57 columns) | 0.07 | 44.0% | OOF AUC 0.7987 (raw), same profit table as v1, default rate among approved about 3.5% | not uploaded | recommended candidate |
| cand_clean_t12 | same | same | 0.12 | 62.5% | same model | not uploaded | recommended candidate |
| cand_t20 | same | same | 0.20 | about 79% | same model; aggressive | not uploaded | candidate (not planned for upload) |

Rules: 5 submissions per day; up to 2 final submissions. A cutoff is not chosen
from the public leaderboard alone: leaderboard results are used only as extra
evidence about the hidden profit formula, alongside the cross-validated
scenario table. Final/private submission selection needs Kish's explicit approval.

Notes: the `clean` candidates make the same decisions as the `no_rate`
candidates for 97.3% of applicants (predicted-PD correlation 0.995) at both
cutoffs, so they are near-duplicates in expectation; `clean` is preferred because
it removes fields that could be proxies or post-decision information at no
measurable accuracy cost.

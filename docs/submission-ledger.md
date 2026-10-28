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

## Format fix before any upload (2026-10-28)

The first candidate files wrote `LOAN_ID` as floats (for example `264002.0`)
because SAS numerics arrive as floats. They were never uploaded. `submission.build`
now writes integer IDs and `submission.validate` requires integer-typed IDs
(`test_submission_ids_are_written_as_integers`). The files were regenerated from the
saved predictions (no refit) and re-downloaded. Checks on the downloaded files:
header `LOAN_ID,APPROVED`, 100,000 rows, unique integer IDs, only 0/1 values.

| File | Rows | Approval rate | Public LB ($M) |
|---|---|---|---|
| cand_clean_t07.csv | 100,000 | 43.98% | 34.812 |
| cand_clean_t12.csv | 100,000 | 62.55% | 47.159 (public rank 56 at the time) |

## Public leaderboard results (reported by Kish, uploaded by Kish)

- cand_clean_t12 (cutoff 0.12): public score 47.159, rank 56 at that time.
- cand_clean_t07 (cutoff 0.07): public score 34.812.

Reading: the more permissive cutoff earned more. The public metric moves with the
profit assumption, and this agrees with the "total interest" scenarios in
`experiment-log.md`, where the best cutoffs lie between 0.12 and 0.38 and 0.07 is the
most defensive choice. The leaderboard is used only as additional evidence about the
hidden formula, together with the cross-validated scenario table, not on its own.

Comparison with the cross-validated scenario table (profit in $M over all 100K
training loans, `experiment-log.md`):

| Cutoff | Observed public | tot, LGD 0.3 | tot, LGD 0.5 | tot, LGD 0.7 |
|---|---|---|---|---|
| 0.07 | 34.812 | 85.5 | 78.9 | 72.4 |
| 0.12 | 47.159 | 119.8 | 106.4 | 93.0 |
| ratio 0.12 / 0.07 | 1.355 | 1.401 | 1.348 | 1.285 |

The observed ratio 1.355 is closest to the "total interest gain, loss about half the
principal" scenario (1.348); the absolute level then implies the public split is
about 44% of the profit scale (observed / 106.4). This is a two-point fit, so it is
suggestive only: it cannot separate LGD 0.4-0.5 from other formula shapes. Under that
scenario the profit curve is nearly flat between cutoffs 0.15 and 0.25 and peaks near
0.2-0.25, so the next probes to consider (not yet uploaded) are 0.20 and 0.25, with
0.16 as a cautious step. The CV scenario table, not the leaderboard alone, drives the
final choice.

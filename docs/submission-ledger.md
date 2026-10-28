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
| cand_clean_t20.csv | 100,000 | 78.59% | 53.935 |
| cand_clean_t25.csv | 100,000 | 84.43% | 54.290 |

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

## Scenario calibration from the two public scores (clean ensemble, OOF profit in $M)

Profit of the clean ensemble on the 100K training loans, gain = total scheduled
interest, loss = LGD x LOAN_AMOUNT:

| LGD | 0.07 | 0.12 | 0.16 | 0.20 | 0.25 | 0.30 | 0.35 |
|---|---|---|---|---|---|---|---|
| 0.3 | 85.1 | 119.7 | 134.4 | 143.0 | 148.1 | 150.7 | 151.6 |
| 0.4 | 81.8 | 113.3 | 125.2 | 131.4 | 134.1 | 134.5 | 133.7 |
| 0.5 | 78.6 | 106.4 | 116.0 | 119.8 | 120.8 | 118.3 | 115.8 |
| 0.7 | 72.1 | 93.0 | 97.5 | 96.7 | 91.9 | 85.9 | 80.0 |

With LGD 0.5, public score / OOF profit is 34.812 / 78.6 = 0.4429 at cutoff 0.07
and 47.159 / 106.4 = 0.4432 at cutoff 0.12: the same scale factor, which is what a
correct formula shape plus a fixed public share of the data should give (LGD 0.4
and 0.7 do not match the ratio: 1.385 and 1.29 vs observed 1.355). Predicted public
scores under that fit (0.443 x profit): cutoff 0.16 about 51.4, 0.20 about 53.1,
0.25 about 53.5, 0.30 about 52.4. This is a fit to two points and must be confirmed
by the next probe; the CV table remains the basis for the final choice.

Candidate files generated in VFL from the saved clean predictions (not downloaded,
not uploaded): cutoff 0.16 (approval 72.1%), 0.20 (78.6%), 0.25 (84.4%).

## Probes 3 and 4 (reported by Kish from the Kaggle submissions page)

| Submission | Cutoff | Approval | Public score ($M) | Fit prediction (0.443 x OOF profit, LGD 0.5) |
|---|---|---|---|---|
| cand_clean_t07 (uploaded twice, 34.812 both times) | 0.07 | 43.98% | 34.812 | 34.8 (fitted) |
| cand_clean_t12 | 0.12 | 62.55% | 47.159 | 47.1 (fitted) |
| cand_clean_t20 | 0.20 | 78.59% | 53.935 | about 53.1 |
| cand_clean_t25 | 0.25 | 84.43% | 54.290 | about 53.5 |

All 5 submissions of the day are used: t07 twice, t12, t20, t25. The duplicate t07
upload carries no new information (identical score).

Reading: the two fitted points predicted the shape. Both new scores came out about
0.8 higher than predicted, and the gain from 0.20 to 0.25 is only +0.355 (predicted
+0.4), so the profit curve is flattening near its peak. Score / OOF profit is now
53.935 / 119.8 = 0.450 and 54.290 / 120.8 = 0.449 (LGD 0.5), slightly above the
0.443 from the first two points. Matching both the 0.12 -> 0.20 ratio (observed
1.144; LGD 0.5 gives 1.126, LGD 0.4 gives 1.160) and the 0.20 -> 0.25 ratio
(observed 1.0066; LGD 0.5 gives 1.008, LGD 0.4 gives 1.021) points to an effective
loss rate of about 0.45-0.5 of the loan amount under the total-interest gain model.
In that region the CV curve peaks around 0.25-0.30 and is flat within about 1%, so
cutoffs of 0.25 and a bit above (for example 0.28-0.30) are close to optimal; the
gain left to harvest is small (under 1 point). cand_clean_t16.csv (approval 72.10%)
was also downloaded and validated; no submissions remain today.

## Fine cutoff check around the peak (clean ensemble OOF profit, $M, gain = total interest)

| LGD | 0.20 | 0.22 | 0.25 | 0.28 | 0.30 | 0.32 | 0.35 |
|---|---|---|---|---|---|---|---|
| 0.4 | 131.4 | 132.9 | 134.1 | 134.5 | 134.5 | 134.0 | 133.7 |
| 0.45 | 125.6 | 126.6 | 127.0 | 126.8 | 126.4 | 125.9 | 124.8 |
| 0.5 | 119.8 | 120.2 | about 120.8 | about 120 | 118.3 | about 117 | 115.8 |

For an effective loss rate between 0.4 and 0.5 the curve peaks at 0.25-0.28 and then
falls or stays flat, so a 0.30 cutoff is expected to add at most a fraction of a point
over 0.25 and could lose about one point. A cand_clean_t30.csv file (approval 88.5% on
the scoring table) exists in VFL (not downloaded, not uploaded). 0.25 is already within
about 1% of the estimated optimum.

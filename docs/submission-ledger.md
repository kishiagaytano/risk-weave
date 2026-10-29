# Submission ledger

> **Status (2026-10-29):** best public score 54.429 (`cand_clean_rule50`); suggested finals `cand_clean_rule50` and
> `cand_clean_t25`. Early table rows for `cand_t07/t12/t20` refer to the earlier `no_rate` model and were not uploaded.
> SHA-256 checksums: `submission-checksums.md`.


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

## Probe files prepared for the next submission day (not yet uploaded)

| File | Rule | Approval | Predicted public score |
|---|---|---|---|
| cand_clean_rule50.csv | per-loan expected profit, gain = total interest, loss = 50% of loan, clean-model PD | 82.47% | about 54.4-54.6 (actual 54.429) |
| cand_clean_t28.csv | single PD cutoff 0.28, clean model | 87.03% | about 54.0-54.5 (actual 53.924) |

Both were downloaded to the user's Downloads folder and validated (header
`LOAN_ID,APPROVED`, 100,000 unique integer IDs, 0/1 only). Plan: upload rule50 first,
then t28; stop there. Final selection (up to 2) is Kish's choice; suggested:
cand_clean_t25 plus the better of rule50 and t28.

## Probes 5 and 6 (reported by Kish on 2026-10-29)

| Submission | Approval | Public score ($M) | Prediction |
|---|---|---|---|
| cand_clean_rule50 | 82.47% | **54.429** (best so far) | 54.4-54.6 |
| cand_clean_t28 | 87.03% | 53.924 | 54.0-54.5 |

Reading: the per-loan rule scored +0.139 over the best single cutoff (t25 = 54.290),
inside the predicted range and matching the CV estimate (+0.2%). Cutoff 0.28 scored
below 0.25 (-0.366), so the cutoff curve peaks near 0.25 as the CV table indicated;
cutoffs above 0.25 only lose. The fitted formula (gain = total interest, loss about 50%
of the loan, public scale about 0.45) predicted both results to within about 0.2-0.5,
which supports its use for the final decision, although a two-to-six-point fit still
cannot prove the formula. Remaining gain is estimated below 1 point and below public
noise (about 1.0). Suggested finals (Kish's choice): cand_clean_rule50 (54.429) and
cand_clean_t25 (54.290), one rule-based and one cutoff-based file. No final selection
has been made.

## Probe 7: 10-seed bagged rule (reported by Kish on 2026-10-29)

| Submission | Approval | Public score ($M) |
|---|---|---|
| cand_clean_rule50_bag (same rule as rule50, 10-seed averaged model) | 82.42% | 54.370 |
| cand_clean_rule50 (single seed) | 82.47% | 54.429 (still the highest) |

The bagged file scored 0.059 below the single-seed file. 616 of 100,000 applicants (0.62%) have
different decisions, and the expected difference was 0 +-0.1 (seed spread about +-0.05 plus
decision-set noise), so this is noise, not evidence that bagging hurts or that the single seed is
better. The public ranking of the two files is not a reason to prefer one seed over another; the
private 60% decides. Current public ranking of our files: rule50 54.429, rule50_bag 54.370, t25 54.290,
t20 53.935, t28 53.924, t12 47.159, t07 34.812. Suggested finals unchanged: cand_clean_rule50 and
cand_clean_t25 (a cutoff-based and a rule-based file); cand_clean_rule50_bag is an acceptable
lower-variance substitute for rule50 if Kish prefers it. Final selection is Kish's choice.

## Candidate 9: uncertainty-adjusted rule `cand_clean_unc1` (2026-10-29, public score 54.265)

Built to replace `cand_clean_t25` as the second proposed final (rule50 stays the first). Rule: approve when
`(1 - p') x gain > p' x 0.5 x loan amount` with `p'` = equal-weight ensemble PD + 1 x the standard deviation of the three
member PDs (clipped to [0, 1]); gain = monthly payment x term - loan amount. Members disagree most where the model is
least sure, so those loans are held to a higher bar.

Public score (reported by Kish on 2026-10-29): **54.265**, versus 54.290 for `cand_clean_t25` and 54.429 for `cand_clean_rule50`. The gaps (0.025 to `t25`, 0.164 to rule50) are well inside public sampling noise (about 1.0), so the public score neither supports nor contradicts the out-of-fold ranking; the private 60% decides.

Out-of-fold evaluation (saved `rw/oof` arrays, 100,000 training loans; efficiency = profit as a share of the best
achievable at each loss fraction, loss fractions 0.3-0.7, gain = total interest):

| Variant | OOF approval | Differs from rule50 | Profit at loss 0.5 ($M) | Mean efficiency | Worst efficiency |
|---|---|---|---|---|---|
| rule50 | 81.8% | 0 | 120.92 | 0.9834 | 0.9667 |
| t25 | 83.6% | 4.6% | 120.33 | 0.9775 | 0.9490 |
| rule, loss 0.4 | 86.6% | 4.9% | 119.72 | 0.9693 | 0.9078 |
| rule, loss 0.6 | 77.5% | 4.3% | 120.09 | 0.9797 | 0.9384 |
| uncertainty +0.5 sd | 80.6% | 1.2% | 120.73 | 0.9828 | 0.9589 |
| **uncertainty +1 sd (`unc1`)** | **79.3%** | **2.5%** | **120.39** | **0.9809** | **0.9501** |
| uncertainty +2 sd | 76.8% | 5.0% | 119.48 | 0.9750 | 0.9316 |
| rule50 and PD < 0.30 / 0.35 | 81.6% / 81.8% | 0.2% / 0.0% | 120.93 / 120.92 | 0.9837 / 0.9835 | 0.9657 / 0.9667 |
| member weights 0.2/0.4/0.4 (LR/XGB/XGB) | 81.7% | 0.6% | 120.81 | 0.9826 | 0.9658 |
| member weights 0.5/0.25/0.25 | 81.9% | 0.7% | 120.66 | 0.9812 | 0.9628 |

Reading: no variant beats rule50 under the fitted formula (it is the optimum of its own scenario), so the second final
is chosen for diversification: among variants that differ from rule50 on 2-8% of applicants, `unc1` has the best mean
efficiency and worst-case efficiency, and beats `t25` on both. Cost: lower approval than `t25` (80.2% vs 84.4% on the
scoring file).

Scoring-file facts (100,000 applicants): approvals rule50 82,469, unc1 80,234, t25 84,429. Applicants approved by A only /
by B only: rule50 vs unc1 2,235 / 0 (unc1 is a strict subset of rule50); rule50 vs t25 1,293 / 3,253; unc1 vs t25 678 /
4,873. The scoring-side member PDs reproduce the SHA-256 of `cand_clean_rule50` exactly, so the same members and rule
were used for the scoring file as for the submitted rule50.


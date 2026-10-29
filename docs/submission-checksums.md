# Candidate submission checksums

The candidate files themselves are never committed (no CSV, no `LOAN_ID`s, no competition
data in this repository; `.gitignore` excludes every `*.csv`). This list identifies each file
by SHA-256 so an uploaded file can be matched to the version evaluated here.

All files: header `LOAN_ID,APPROVED`, 100,000 rows, unique integer IDs, only 0/1 values, LOAN_IDs in the
scoring-table order. Model: clean 57-column ensemble (logistic regression + XGBoost depth 2 + depth 3,
equal weights). Public scores were reported by Kish from the Kaggle submissions page.

| File | Decision rule | Approval rate | Public score ($M) | SHA-256 |
|---|---|---|---|---|
| cand_clean_t07.csv | PD cutoff 0.07 | 43.98% | 34.812 | `5c62f0bd05afb33360641ea96a837a494479fbbda18c70f2ad350e2ac95bd00f` |
| cand_clean_t12.csv | PD cutoff 0.12 | 62.55% | 47.159 | `11f0e6dd4a4f019decdbfec640048d7fe90aacbbdf1b0750558d2708cdd5c8cd` |
| cand_clean_t16.csv | PD cutoff 0.16 | 72.10% | not uploaded | `505c6559084d0c645fda60376de6129da68ab12d41fd03dc2d1a400e3a64208e` |
| cand_clean_t20.csv | PD cutoff 0.20 | 78.59% | 53.935 | `c82526c94ed21f2033c6a08217b24b9b06431e5dba8074bb80a0ce2945bb44ff` |
| cand_clean_t25.csv | PD cutoff 0.25 | 84.43% | 54.290 | `99315129c12c38173e8657f6658236fb0a859162393dc5d92324ee01bb6d7d63` |
| cand_clean_t28.csv | PD cutoff 0.28 | 87.03% | 53.924 | `55e5d612182eabaae042617781c37efe3d8a3d8f9b1375c91a478f2b2567ef47` |
| cand_clean_rule50.csv | per-loan expected profit, loss 50% of loan | 82.47% | 54.429 | `2189c097ee2aa222599fc6d730e0ba696f64567ed3248d717c8f1f7b07670cd0` |
| cand_clean_rule50_bag.csv | same rule, 10-seed averaged model | 82.42% | 54.370 | `01ec8aa389aca5d2ddca62754da4056e726ca6947c97968aa1e73a48e5cda87f` |
| cand_clean_unc1.csv | per-loan expected profit (loss 50%) on an uncertainty-adjusted PD: ensemble PD + 1 x std of the three member PDs | 80.23% (scoring file) | 54.265 | `821d76d896fb4642e5eb304f5a7ac94be6a048c85d52ab1714cd6ef62cd6323a` |
| cand_clean_fit70m18.csv | per-loan expected profit with loss = 70% of (loan - 18 monthly payments) | 83.51% (scoring file) | **54.463** (highest so far) | `f855bec552e1185cdabbd04e5f726926cff4b733ffe0866b058de2f555a81c9f` |
| cand_clean_fitA80k23.csv | per-loan expected profit with loss = 80% of (loan - 23 monthly payments) | 83.67% (scoring file) | not uploaded | `e315da349df6126baed81ae269b796ae7a0685028da403e77e680bdbfda703d1` |

cand_clean_t30.csv (cutoff 0.30, 88.5% approved) exists only in the SAS Viya home folder (`rw/submissions`)
and was neither downloaded nor uploaded, so it has no checksum here. The same files were downloaded to the
user's `Downloads` folder, outside this repository. To re-verify a file on Windows:
`certutil -hashfile <file> SHA256`.

cand_clean_unc1.csv was built in VFL on 2026-10-29 (`rw/submissions`) and downloaded to `Downloads`; the SHA-256 above was computed on the downloaded file. Its approval rate is on the scoring file; on the out-of-fold training data (saved `rw/oof` arrays) the same rule approves 79.3%. Format check: header `LOAN_ID,APPROVED`, 100,000 rows, 100,000 unique integer IDs, only 0/1.

cand_clean_fit70m18.csv (2026-10-29; public score 54.463 reported by Kish, the highest of our files) is built from a loss formula refitted to the public scores (see `submission-ledger.md`, candidate 10). Downloaded to `Downloads`; the SHA-256 was computed on the downloaded copy. Format check: header `LOAN_ID,APPROVED`, 100,000 rows, 100,000 unique integer IDs, only 0/1.

cand_clean_fitA80k23.csv (2026-10-29) was built in VFL and downloaded to `Downloads` after the nine-point formula refit (see `submission-ledger.md`, candidate 11); the SHA-256 above was computed on the downloaded copy. Format check: header `LOAN_ID,APPROVED`, 100,000 rows, 100,000 unique integer IDs, only 0/1. (`cand_clean_fitA80k23u.csv`, the uncertainty-adjusted variant, stays in the VFL home folder only and is not downloaded.)

# How SAS Viya for Learners (VFL) was used

Everything that touches competition data ran inside SAS Viya for Learners. The Kaggle sample files (10 rows
each) were used only to check file formats and to test code locally. No credentials, host names or personal
information are recorded here; open the platform from the competition's Learning Portal.

## What ran where

| Stage | Tool inside VFL | Detail |
|---|---|---|
| Data location | Manage Data (SAS Data Explorer) | Two in-memory CAS tables in one caslib: the 100,000-row training table (83 columns) and the 100,000-row scoring table (82 columns, no `DEFAULT`). |
| Profiling | SAS Studio, SAS program | `PROC CONTENTS`, `PROC FREQ`, `PROC MEANS`, `PROC SQL` against the CAS tables; verbatim in `sas-viya-commands.sas`, findings in `sas-viya-observations.md`. |
| Modelling | SAS Studio, **Python program** (`PROC PYTHON`) | pandas, numpy, scikit-learn and XGBoost provided by the platform (no LightGBM, CatBoost or SHAP). Tables are read with `SAS.sd2df`. 5-fold CV, ensemble, policy analysis, final fit and scoring. |
| Baseline | **Model Studio** | Project `RiskWeave_Baseline` on the training table: target `DEFAULT`, the same excluded variables set to role *Rejected*, pipeline Data -> Gradient Boosting and Logistic Regression (stepwise) -> Model Comparison. Reference only. |
| Outputs | SAS home folder (`rw/`) | Out-of-fold and scoring predictions (`rw/oof`), experiment log (`rw/experiment_log.jsonl`), candidate submission files (`rw/submissions`), the installed package (`rw/risk_weave`). |

No source table was modified. Tables were only read; temporary copies lived in Python memory or the temporary
WORK library of the compute session.

## Re-running the workflow

1. **Open** SAS Studio from the VFL landing page and start a *Python program*.
2. **Install the package** into your home folder. Locally, in a clone of this repository:
   `python tools/pack_for_vfl.py --install` prints a short script (several lines); paste it into the Python program and
   run it. It writes `~/rw/risk_weave/*.py`. (Long single lines and auto-indenting make pasting the source files
   directly unreliable, which is why the packer exists; it only compresses and writes the repo code.)
3. **Connect to CAS** in a Python program (the compute session can lose its libref between runs, in which case
   `SAS.sd2df` returns an empty frame):
   ```python
   import os, sys
   sys.path.insert(0, os.path.expanduser('~/rw'))
   SAS.submit('libname creditr clear; cas rw1; libname creditr cas caslib=CREDITr sessref=rw1;')
   from risk_weave import data, pipeline
   train = SAS.sd2df(data.VFL_TRAIN)
   score = SAS.sd2df(data.VFL_SCORE)
   ```
4. **Run the workflow** (about 5-10 minutes; keep each run under a few minutes if the server is busy, as long runs can
   hit a session timeout, in which case use the "Reset SAS session" link and re-run):
   ```python
   out = os.path.expanduser('~/rw/submissions')
   result = pipeline.run_all(train, score, out_dir=out, log_path=os.path.expanduser('~/rw/experiment_log.jsonl'))
   print(result['cv'], result['approval'])
   ```
   This reproduces the cross-validation of the three members, the final fit on all 100,000 rows, and validated files
   for the per-loan rule and the 0.20 / 0.25 cutoffs (the same decisions as `cand_clean_rule50`, `cand_clean_t20`,
   `cand_clean_t25` up to the default seed; the bagged variants used 10 seeds, see `experiment-log.md`).
5. **Download only the final submission files** from *Files > Home > rw > submissions* (right-click > Download).
6. **Model Studio baseline** (optional): create a project on the training table, set `DEFAULT` as target, set the
   excluded variables to *Rejected* (list in `SOLUTION.md`), add Gradient Boosting and Logistic Regression
   under the Data node, run, and compare on the Pipeline Comparison tab.

## Notes
* Python inside SAS Studio keeps its state between runs of the same session; a reset clears it. Everything needed to
  rebuild state is on disk under `rw/`.
* Only aggregate statistics and the submission files left the platform. Competition data is not redistributed.

---

# Detailed VFL walkthrough

Everything below was done in SAS Viya for Learners (VFL). Only aggregates and the final submission files left the
platform; competition data stayed in the CAS library.

## A. Navigation and objects
| Object | Where / name |
|---|---|
| Entry | The competition's Learning Portal opens the VFL landing page; sign in with the participant's own account (credentials are never stored in this repository). |
| Data | *Manage Data* (SAS Data Explorer) -> caslib `CREDITr`; tables `ILINK_CREDITRISK_TRAINING` (100,000 x 83, has `DEFAULT`) and `ILINK_CREDITRISK_SCORING` (100,000 x 82). Loaded in memory (CAS), read-only use. |
| Code | *Develop Code and Flows* = SAS Studio. Two program types were used: **SAS program** (profiling) and **Python program** (modelling, runs through `PROC PYTHON`; the `SAS` object gives `SAS.sd2df`, `SAS.submit`). |
| Baseline | *Build Models* = Model Studio, project `RiskWeave_Baseline` (stored in My Folder). |
| Files | *Files > Home*: `rw/risk_weave` (installed package), `rw/oof` (out-of-fold predictions), `rw/submissions` (candidate CSVs), `rw/experiment_log.jsonl`, `rw/importance_aggregates.json`. |

## B. Stage-by-stage record
1. **Data audit (SAS program).** `PROC CONTENTS`, `PROC FREQ`, `PROC MEANS`, `PROC SQL` on both tables: row counts,
   uniqueness of `LOAN_ID`, target rate 13.48%, missingness, train/scoring comparison. Code: `sas-viya-commands.sas`;
   results: `sas-viya-observations.md`.
2. **Package installation (Python program).** `python tools/pack_for_vfl.py --install` (run locally) prints a short
   script made of many short `bN='...'` lines (base64 + zlib chunks, no line longer than the editor's wrapping limit)
   that writes `~/rw/risk_weave/*.py`. Pasting full source files directly failed (long lines, auto-indent, auto-closed
   quotes), hence the packer; it only compresses the repository code and writes it back byte-for-byte.
3. **Connect to CAS and read tables (Python program).** `SAS.submit('libname creditr clear; cas rw1; libname creditr cas
   caslib=CREDITr sessref=rw1;')`, then `data.load_vfl(data.VFL_TRAIN, SAS)`. If `SAS.sd2df` returns an empty frame
   the libref was lost between runs: re-submit the `libname` statement (a guard in `load_vfl` raises on empty reads).
4. **Cross-validation.** `pipeline.cross_validate`: 5 stratified folds (seed 20261028) for each member (logistic
   regression C=0.1; XGBoost depth 2, 800 trees, learning rate 0.05; XGBoost depth 3, 500 trees, learning rate 0.04,
   min child weight 20, lambda 10) on the 57 `clean` columns; out-of-fold probabilities saved under `rw/oof`;
   ensemble = equal-weight mean. Result: AUC 0.7987.
5. **Policy analysis.** Out-of-fold profit under eight documented loss/interest scenarios, cutoff curves, the per-loan
   rule (`policy.py`, `pipeline.decisions`), group approval and default tables (`fairness-and-explainability.md`).
6. **Final fit and scoring.** `final.fit_predict` refits the three members on all 100,000 rows and scores the 100,000
   scoring loans; `final.candidate` / `submission.build` write `LOAN_ID,APPROVED` with integer IDs and
   `submission.validate` checks row count, unique IDs matching the scoring table and 0/1 values.
7. **Experiments.** Weighted training, profit-aware XGBoost, stacking, engineered ratios, collateral-aware loss, and
   seed bagging; all logged in `rw/experiment_log.jsonl` and `experiment-log.md`.
8. **Importance analysis (2026-10-29).** 80/20 stratified split (seed 20261028), members refit on 80%, permutation
   importance on the holdout (3 shuffles per column, seed 20261029), XGBoost total-gain shares and native TreeSHAP
   (`Booster.predict(..., pred_contribs=True)`, 5,000 holdout rows), aggregated to the original columns; results in
   `fairness-and-explainability.md`. The `shap` package is not available in VFL and was not used.
9. **Model Studio baseline.** New project on the training table, target `DEFAULT` (binary), excluded variables set to
   role *Rejected* (sensitive, `INTEREST_RATE`, proxy-capable and timing-uncertain lists in `SOLUTION.md`), pipeline
   Data -> Gradient Boosting and Logistic Regression (stepwise) -> Model Comparison. Reference only; the submitted
   decisions come from the Python ensemble.
10. **Download.** Right-click the file in *Files > Home > rw > submissions* -> Download; the SHA-256 is compared with
    `submission-checksums.md`.

## C. Timings and limits seen
| Step | Typical wall time |
|---|---|
| Package install | seconds |
| 5-fold CV for three members | about 2-5 minutes |
| Final fit + scoring (one seed) | about 1-2 minutes |
| 10-seed bagged refit | needed two runs of 5 seeds (single run hit the compute-session timeout) |
| Importance analysis (permutation over 57 columns x 3 shuffles) | about 2 minutes |

## D. Pitfalls and fixes
| Symptom | Cause | Fix |
|---|---|---|
| `SAS.sd2df` returns 0 rows | CAS libref dropped between submissions | re-submit the `libname creditr cas ...` line |
| "The SAS session is no longer valid" / timeout | compute session limit during a long run | *Reset SAS session*, split the work, write parts to `rw/oof` |
| Typed code is corrupted (merged lines, extra quotes) | editor line wrapping, auto-closing quotes, auto-indent | short single-line statements, `for ...: a; b` one-liners, or the packer installer |
| Blue loading screen, JavaScript truncated | server or hidden-window stall | reload the tab; use the "Return to application" link on the timeout page |
| Float IDs such as `264002.0` in a candidate | `LOAN_ID` read as float | `submission.build` casts to int64; `validate` requires integer dtype (tested) |
| Package state vanished | session reset | state is rebuilt from `rw/` on disk |

## E. Data-handling rules observed
* Tables were only read; no source table was modified or exported.
* No row-level or ID-level data was copied into this repository; only aggregates (importances, group tables, scores)
  and SHA-256 checksums are documented.
* The only files downloaded were the candidate submission CSVs, which are git-ignored.

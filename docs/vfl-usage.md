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

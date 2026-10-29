# Reproducibility

What can be reproduced, from which inputs, with what tolerance, and what cannot be.

## 1. Inputs
* **Data**: the competition training table (100,000 rows, 83 columns, `DEFAULT` target) and scoring table (100,000
  rows, 82 columns), read from the CAS library in SAS Viya for Learners. They are not in this repository and may not
  be redistributed. Four small Kaggle sample files exist locally for format checks only and are git-ignored.
* **Code**: `src/risk_weave` at the commit being checked out (this repository is the single source).
* **Software**: VFL versions in `vfl-environment.md`; local development versions in `requirements-lock.txt`.

## 2. Determinism controls
| Source of randomness | Control |
|---|---|
| Cross-validation folds | `StratifiedKFold(5, shuffle=True, random_state=SEED)`, `SEED = 20261028` in `config.py` (isotonic calibration folds use SEED+1, stacking SEED+7) |
| Logistic regression | deterministic solver (lbfgs), no randomness |
| XGBoost | `random_state=SEED` (20261028) in `models.xgboost`, `tree_method="hist"`, `n_jobs=-1`; multi-threaded floating-point summation order can differ across thread counts and library versions, which is why byte equality is only claimed on the same VFL image |
| Seed bagging (experiment only) | seeds 11-14 (4-seed OOF check) and 21-30 (10-seed final refit) in `experiment-log.md`; the selected files use the single default seed |
| Bootstrap resamples (robustness table) | `numpy.random.default_rng` with fixed seeds, as recorded in `experiment-log.md` |
| Importance analysis | split seed 20261028, permutation seed 20261029 |

No seed was chosen using the public leaderboard.

## 3. Levels of reproduction
1. **Tests (anywhere, seconds)**: `python -m pytest -q` runs 16 tests on a synthetic frame: format validation,
   integer IDs, feature sets exclude sensitive and proxy columns, policy maths, end-to-end `pipeline.run_all`.
   CI (GitHub Actions) runs the same tests on every push.
2. **Pipeline on VFL (about 5-10 minutes)**: install the package and call `pipeline.run_all` (details in
   `vfl-usage.md`). Expected: cross-validated ensemble AUC 0.7987 and approval 82.5% for `rule50` (83.5% for `fit70m18`; the final pair is described in `final-submissions.md`).
3. **Byte-identical files**: compare SHA-256 values of the produced files with `submission-checksums.md`.
   Byte equality requires the VFL image versions of `vfl-environment.md`. On other versions the AUC reproduces to
   about the fourth decimal, but a handful of borderline loans (well under 1%) can flip.

## 4. What is recorded
| Item | Where |
|---|---|
| Every experiment with metrics | `experiment-log.md`, `experiment_log.jsonl` in the VFL home folder (not committed) |
| Exact commands run in SAS | `sas-viya-commands.sas`, `vfl-usage.md` |
| Candidate files, public scores, hashes | `submission-ledger.md`, `submission-checksums.md` |
| Final selection and reasons | `final-submissions.md` |
| Package versions | `vfl-environment.md`, `requirements-lock.txt` |
| Feature sets and exclusions | `src/risk_weave/config.py`, `fairness-and-explainability.md` |

## 5. Known limits
* VFL versions were recorded after the modelling runs (2026-10-29). No upgrade was observed but cannot be proven.
* The hidden metric is not published; the profit rule's loss fraction (0.5) is inferred from public scores.
* Importance figures were computed on an 80/20 holdout refit, not the final all-rows model.
* Local and VFL library versions differ slightly (see `vfl-environment.md`); the code was written to use only stable APIs.

## 6. Checklist for a reviewer
```bash
git clone https://github.com/kishiagaytano/risk-weave.git && cd risk-weave
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements-lock.txt
.venv/Scripts/python -m pytest -q          # expect 16 passed
.venv/Scripts/python tools/pack_for_vfl.py --install > install_in_vfl.txt   # script to paste into SAS Studio
```
Then follow `vfl-usage.md` inside SAS Viya for Learners and compare checksums.

# Risk Weave

[![tests](https://github.com/kishiagaytano/risk-weave/actions/workflows/tests.yml/badge.svg)](https://github.com/kishiagaytano/risk-weave/actions/workflows/tests.yml)

Auto-loan approval decisions for the **SAS Hackathon 2026 Student Track** (iLink Capital Bank).
Risk Weave estimates each applicant's probability of default, then turns that estimate into an
explicit approve / do-not-approve decision by weighing the interest a loan would earn against the
principal it could lose. Everything was built and run in **SAS Viya for Learners** (SAS Studio Python,
CAS tables, a Model Studio baseline) and is packaged here as tested, reproducible code.

## Result at a glance

| | |
|---|---|
| Model | Equal-weight ensemble of regularised logistic regression + XGBoost (depth 2) + XGBoost (depth 3) |
| Inputs | 57 "clean" columns: no race, gender, age or marital status; no interest rate; no proxy-prone or timing-uncertain fields |
| Validation | 5-fold stratified cross-validation on 100,000 labelled loans: AUC 0.7987, well calibrated (ECE about 0.001-0.002) |
| Decision | Approve when `(1 - PD) x interest > PD x 0.5 x loan amount` (per-loan expected profit) |
| Best public score | **54.429** (`cand_clean_rule50`); single-cutoff hedge `cand_clean_t25` = 54.290 |
| Fairness | Default rate among approved loans stays 6.2-10.2% across every demographic level; lowest approval ratios: state tier 0.83, employment 0.83, education 0.77 (details in `docs/fairness-and-explainability.md`) |

The competition metric is withheld, so the profit assumptions (interest earned if repaid, a fraction of the
loan lost on default) were inferred from the first public scores and cross-checked against cross-validation;
see `docs/SOLUTION.md`. The public leaderboard served as additional evidence about the metric when choosing the decision
rule and cutoff; the model itself and its random seeds were not tuned to it.

## Public leaderboard probes

| File (not committed) | Rule | Approved | Public score |
|---|---|---|---|
| `cand_clean_rule50` | per-loan rule, loss 0.5 | 82.47% | **54.429** |
| `cand_clean_rule50_bag` | same rule, 10-seed average | 82.42% | 54.370 |
| `cand_clean_t25` | PD < 0.25 | 84.43% | 54.290 |
| `cand_clean_t20` | PD < 0.20 | 78.59% | 53.935 |
| `cand_clean_t28` | PD < 0.28 | 87.03% | 53.924 |
| `cand_clean_t12` | PD < 0.12 | 62.55% | 47.159 |
| `cand_clean_t07` | PD < 0.07 | 43.98% | 34.812 |

SHA-256 checksums are in `docs/submission-checksums.md`. Submission files themselves, the Kaggle sample
files and all VFL data are deliberately **not** in this repository (competition rules: data may not be
shared outside the competition).

## Quick start

```bash
git clone https://github.com/kishiagaytano/risk-weave.git && cd risk-weave
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements-lock.txt   # Linux/macOS: .venv/bin/python
python -m pytest -q          # 15 tests on synthetic data, no competition data needed
```

Run the whole workflow on any train/scoring pair of frames:

```python
from risk_weave import data, pipeline
train, score = data.load_csv("train.csv"), data.load_csv("score.csv")      # or SAS.sd2df(...) in SAS Viya
result = pipeline.run_all(train, score, out_dir="out/")                     # audit, 5-fold CV, final fit,
print(result["cv"], result["approval"])                                     # validated submission files
```

## How SAS Viya for Learners was used

1. **Data**: the 100,000-row training and scoring tables live in a CAS library and never left the platform
   except the final submission files.
2. **SAS Studio (Python)**: all modelling ran here with the platform's scikit-learn and XGBoost. The package
   in `src/risk_weave` is installed into the SAS home folder with `python tools/pack_for_vfl.py --install`
   (a compressed one-line installer, because long code is hard to paste into the editor) and executed with
   `PROC PYTHON` through `SAS.sd2df` for table access.
3. **Model Studio**: project `RiskWeave_Baseline` (gradient boosting and stepwise logistic regression on the same
   57 inputs) is the reference baseline.
4. **SAS code**: exploratory profiling used SAS procedures, recorded verbatim in `docs/sas-viya-commands.sas`.

Step-by-step instructions to re-run each stage are in `docs/vfl-usage.md`.

## Repository map

| Path | Content |
|---|---|
| `docs/SOLUTION.md` | Judge-facing solution summary: problem, approach, evidence, why the final submissions |
| `docs/fairness-and-explainability.md` | Group outcomes, excluded variables, coefficients, limitations |
| `docs/vfl-usage.md` | Exactly what ran inside SAS Viya for Learners and how to rerun it |
| `docs/model-card.md` | Data, features, model, validation, policy, limitations |
| `docs/experiment-log.md` | Every experiment with metrics |
| `docs/submission-ledger.md`, `docs/submission-checksums.md` | Candidate files, public scores, SHA-256 checksums |
| `docs/competition-rules-and-evaluation.md`, `docs/sas-viya-observations.md` | Rules as read, data audit |
| `docs/INDEX.md` | Reading order and change history |
| `src/risk_weave/` | Package: data, features, models, CV, policy, final fit, extra experiments, pipeline |
| `tests/` | 15 tests on synthetic data |
| `tools/` | `pack_for_vfl.py` (VFL installer), VFL driver snippets |
| `AGENTS.md`, `PROJECT_CONTEXT.md`, `instruction-decisions.md` | Project rules and decisions |

## Limitations and honest notes

- The scoring formula is unpublished; the profit model is inferred and reproduces the public scores to within about 1 point,
  but it is an inference.
- No time dimension exists in the data, so there is no out-of-time validation. Public-leaderboard differences
  below about 1 point are within sampling noise; the final ranking uses the other 60% of the test data.
- Education and employment status are legitimate credit inputs but produce lower approval ratios for some
  groups (education 0.77). This is disclosed, not corrected.
- Package versions inside SAS Viya for Learners were not recorded; local tests use the pinned versions in
  `requirements-lock.txt`.
- No licence is set yet; the owner has not chosen one.

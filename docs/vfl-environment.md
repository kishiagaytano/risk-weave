# SAS Viya for Learners: recorded software environment

Captured on 2026-10-29 from a SAS Studio *Python program* in the same compute session type used for all
modelling (`importlib.metadata.version` for each package; the snippet is at the end of this file).

| Item | Value |
|---|---|
| Python | 3.12.12 |
| OS | Linux 5.15.0, x86_64 |
| CPUs visible to the session | 32 |
| numpy | 2.5.1 |
| pandas | 3.0.3 |
| scikit-learn | 1.9.0 |
| scipy | 1.18.0 |
| xgboost | 3.3.0 |
| statsmodels | 0.14.6 |
| swat | 1.18.1 |
| saspy | 5.108.3 |
| sasctl | 1.11.8 |
| matplotlib | 3.11.0 |
| joblib | 1.5.3 |
| threadpoolctl | 3.6.0 |
| `SAS` object type | `SAS2py` (table access with `SAS.sd2df`) |

Not installed in VFL: `shap`, LightGBM, CatBoost.

## Local versus VFL

The repository was developed and tested locally with the versions in `requirements-lock.txt`
(numpy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1, scipy 1.18.1, xgboost 3.4.1). VFL runs slightly older
patch/minor releases (numpy 2.5.1, pandas 3.0.3, scikit-learn 1.9.0, xgboost 3.3.0). The package only uses stable
APIs, and the 15 tests pass locally; the VFL runs reproduced the cross-validated AUC (0.7987) and the approval rates
recorded in the experiment log. Exact decision-for-decision equality between a local and a VFL run is not claimed:
tree libraries may differ in the last decimals across versions, which can flip a handful of borderline loans.
The submitted files are the ones produced in VFL; their SHA-256 values are in `submission-checksums.md`.

Earlier runs (before this record was made) used the same VFL image; no package upgrade was observed during the
project, but versions were not recorded at the time.

## Snippet used

```python
import sys, platform, importlib.metadata as im
print('python', sys.version.split()[0]); print('os', platform.system(), platform.release()[:12], platform.machine())
for n in ['numpy','pandas','scikit-learn','scipy','xgboost','statsmodels','swat','saspy','sasctl','matplotlib','joblib','threadpoolctl']:
    print(n, im.version(n))
print('cpus', __import__('os').cpu_count())
```

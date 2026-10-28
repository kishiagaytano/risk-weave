from risk_weave import data, config
train = data.load_vfl(data.VFL_TRAIN, SAS)
score = data.load_vfl(data.VFL_SCORE, SAS)
import json
print("AUDIT " + json.dumps(data.audit(train, score), sort_keys=True))
print("PY", __import__("sys").version.split()[0])
for m in ("pandas", "numpy", "sklearn", "xgboost", "scipy"):
    print(m, __import__(m).__version__)

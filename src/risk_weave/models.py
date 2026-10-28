"""Model factories. Only libraries available inside VFL are used."""
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from .config import SEED
from .features import make_preprocessor


def logreg(X, C=0.1, penalty="l2", class_weight=None):
    kw = {"penalty": "l1", "solver": "liblinear"} if penalty == "l1" else {}
    est = LogisticRegression(C=C, max_iter=2000, class_weight=class_weight,
                             random_state=SEED, **kw)
    return Pipeline([("prep", make_preprocessor(X, scale=True)), ("model", est)])


def xgboost(X, **params):
    base = dict(
        n_estimators=400, learning_rate=0.05, max_depth=4, min_child_weight=5,
        subsample=0.8, colsample_bytree=0.8, reg_lambda=5.0, reg_alpha=0.0,
        tree_method="hist", eval_metric="logloss", random_state=SEED, n_jobs=-1,
    )
    base.update(params)
    return Pipeline([("prep", make_preprocessor(X, scale=False)), ("model", XGBClassifier(**base))])


def forest(X, kind="rf", **params):
    base = dict(n_estimators=300, min_samples_leaf=30, max_features="sqrt",
                n_jobs=-1, random_state=SEED)
    base.update(params)
    cls = RandomForestClassifier if kind == "rf" else ExtraTreesClassifier
    return Pipeline([("prep", make_preprocessor(X, scale=False)), ("model", cls(**base))])

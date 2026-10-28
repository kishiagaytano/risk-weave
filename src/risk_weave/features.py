"""Preprocessing shared by every model so folds see identical transforms."""
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def split_types(X):
    cat = [c for c in X.columns if X[c].dtype == object or str(X[c].dtype).startswith(("str", "category"))]
    num = [c for c in X.columns if c not in cat]
    return num, cat


def make_preprocessor(X, scale=False):
    """Median-impute numerics (with missing indicators), one-hot categoricals.

    scale=True standardises numerics (needed by regularised logistic regression).
    """
    num, cat = split_types(X)
    num_steps = [("impute", SimpleImputer(strategy="median", add_indicator=True))]
    if scale:
        num_steps.append(("scale", StandardScaler()))
    cat_steps = [
        ("impute", SimpleImputer(strategy="constant", fill_value="__missing__")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=20, sparse_output=False)),
    ]
    return ColumnTransformer(
        [("num", Pipeline(num_steps), num), ("cat", Pipeline(cat_steps), cat)],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def to_numpy_safe(X):
    """Replace pandas NA markers so SimpleImputer sees plain NaN/str values."""
    X = X.copy()
    for c in X.columns:
        if X[c].dtype == object or str(X[c].dtype).startswith(("str", "category")):
            X[c] = X[c].astype(object).where(X[c].notna(), np.nan)
    return X

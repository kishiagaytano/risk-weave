"""Preprocessing shared by every model so folds see identical transforms."""
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, SplineTransformer, StandardScaler


def split_types(X):
    cat = [c for c in X.columns if X[c].dtype == object or str(X[c].dtype).startswith(("str", "category"))]
    num = [c for c in X.columns if c not in cat]
    return num, cat


def make_preprocessor(X, scale=False, spline_knots=0):
    """Median-impute numerics (with missing indicators), one-hot categoricals.

    scale=True standardises numerics (needed by regularised logistic regression).
    spline_knots>0 expands continuous numerics (>10 distinct values) into cubic
    B-splines so a linear model can fit smooth non-linear effects (GAM-style).
    """
    num, cat = split_types(X)
    cont = [c for c in num if X[c].nunique() > 10] if spline_knots else []
    rest = [c for c in num if c not in cont]
    num_steps = [("impute", SimpleImputer(strategy="median", add_indicator=True))]
    if scale:
        num_steps.append(("scale", StandardScaler()))
    cat_steps = [
        ("impute", SimpleImputer(strategy="constant", fill_value="__missing__")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=20, sparse_output=False)),
    ]
    parts = [("num", Pipeline(num_steps), rest), ("cat", Pipeline(cat_steps), cat)]
    if cont:
        spl = [("impute", SimpleImputer(strategy="median", add_indicator=True)),
               ("spline", SplineTransformer(n_knots=spline_knots, degree=3, knots="quantile",
                                            extrapolation="constant")),
               ("scale", StandardScaler())]
        parts.append(("spline", Pipeline(spl), cont))
    return ColumnTransformer(
        parts,
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

"""Data loading for the two execution environments.

Locally the repository only holds tiny Kaggle sample files (10 rows each), which
are useful for plumbing tests only. Real modeling runs inside SAS Viya for
Learners (VFL), where tables are read with ``SAS.sd2df``.
"""
from pathlib import Path

import pandas as pd

from .config import ID_COL, TARGET

VFL_TRAIN = "CREDITr.ILINK_CREDITRISK_TRAINING"
VFL_SCORE = "CREDITr.ILINK_CREDITRISK_SCORING_PUBLIC"


def load_csv(path):
    return pd.read_csv(Path(path))


def assign_vfl_librefs(sas):
    """(Re)connect a CAS session and the CREDITr libref.

    The compute session can lose its CAS libref between runs, in which case
    ``sd2df`` silently returns an empty frame; the shape check in ``load_vfl``
    catches that.
    """
    sas.submit("libname creditr clear; cas rw1; libname creditr cas caslib=CREDITr sessref=rw1;")


def load_vfl(table, sas, min_rows=1):
    """Read a CAS table through the ``SAS`` object available in PROC PYTHON."""
    df = sas.sd2df(table)
    if df is None or len(df) < min_rows:
        assign_vfl_librefs(sas)
        df = sas.sd2df(table)
    if df is None or len(df) < min_rows:
        raise RuntimeError(f"{table} came back empty; check the CAS session and libref")
    return df


def split_xy(df):
    """Return (features frame, target series or None, ids)."""
    ids = df[ID_COL].copy()
    y = df[TARGET].astype(int) if TARGET in df.columns else None
    return df.drop(columns=[c for c in (ID_COL, TARGET) if c in df.columns]), y, ids


def audit(train, score=None):
    """Compact data-quality summary used by the audit log."""
    out = {
        "n_rows": int(len(train)),
        "n_cols": int(train.shape[1]),
        "id_unique": bool(train[ID_COL].is_unique),
        "dup_rows_ex_id": int(train.drop(columns=[ID_COL]).duplicated().sum()),
        "default_rate": float(train[TARGET].mean()) if TARGET in train else None,
        "missing": {c: int(n) for c, n in train.isna().sum().items() if n},
    }
    if score is not None:
        out["score_rows"] = int(len(score))
        out["score_id_unique"] = bool(score[ID_COL].is_unique)
        out["id_overlap"] = int(len(set(train[ID_COL]) & set(score[ID_COL])))
        out["schema_diff"] = sorted(set(train.columns) ^ set(score.columns))
    return out

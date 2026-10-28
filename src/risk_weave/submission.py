"""Build and validate the required LOAN_ID,APPROVED file."""
import pandas as pd

from .config import ID_COL

COLUMNS = [ID_COL, "APPROVED"]


def build(ids, approved):
    """Build the submission frame. IDs may arrive as floats from SAS numerics;
    they are written as integers (e.g. 264002, not 264002.0)."""
    ids = pd.Series(list(ids))
    if (ids % 1 != 0).any():
        raise ValueError("LOAN_ID values must be whole numbers")
    sub = pd.DataFrame({ID_COL: ids.astype("int64"), "APPROVED": [int(a) for a in approved]})
    return sub[COLUMNS]


def validate(sub, scoring_ids):
    """Raise ValueError unless the file meets the competition format."""
    if list(sub.columns) != COLUMNS:
        raise ValueError(f"columns must be exactly {COLUMNS}, got {list(sub.columns)}")
    if sub[ID_COL].isna().any() or sub["APPROVED"].isna().any():
        raise ValueError("missing values present")
    if not pd.api.types.is_integer_dtype(sub[ID_COL]):
        raise ValueError("LOAN_ID must be integer typed (no 123.0 floats)")
    if not sub[ID_COL].is_unique:
        raise ValueError("duplicate LOAN_ID rows")
    if set(sub["APPROVED"].unique()) - {0, 1}:
        raise ValueError("APPROVED must contain only 0 or 1")
    expected = {int(i) for i in scoring_ids}
    got = set(sub[ID_COL])
    if got != expected:
        raise ValueError(f"LOAN_ID mismatch: {len(expected - got)} missing, {len(got - expected)} extra")
    if len(sub) != len(expected):
        raise ValueError("row count differs from scoring table")
    return True

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(scope="session")
def synthetic():
    """Synthetic stand-in with the real column names used by the pipeline.

    Not real competition data: generated from a seeded random model so tests can
    run without the restricted VFL tables.
    """
    rng = np.random.default_rng(7)
    n = 3000
    amount = rng.uniform(5000, 60000, n)
    rate = rng.uniform(0.03, 0.09, n)
    term = rng.choice([48, 60, 72, 84], n)
    dti = rng.uniform(0.05, 0.6, n)
    ltv = rng.uniform(0.5, 1.0, n)
    income = rng.uniform(20000, 150000, n)
    z = -4.5 + 8 * dti + 40 * (rate - 0.045) + 2 * (ltv - 0.85)
    y = (rng.uniform(size=n) < 1 / (1 + np.exp(-z))).astype(int)
    monthly = amount * (1 + rate * term / 12) / term
    df = pd.DataFrame({
        "LOAN_ID": rng.permutation(np.arange(100, 100 + n)),
        "AGE_BAND": rng.choice(["18-29", "30-44", "45-59", "60+"], n),
        "GENDER": rng.choice(["Female", "Male", "Nonbinary"], n),
        "RACE_ETH": rng.choice(["Asian", "Black", "Hispanic", "Other", "White"], n),
        "MARITAL_STATUS": rng.choice(["Married", "Single"], n),
        "STATE_TIER": rng.choice(["H", "M", "L"], n),
        "AGE_D": rng.integers(18, 79, n).astype(float),
        "EMPLOYMENT_STATUS": rng.choice(["Full-time", "Part-time", "Unemployed"], n),
        "HOUSEHOLD_INCOME": np.where(rng.uniform(size=n) < 0.05, np.nan, income),
        "DEBT_TO_INCOME": dti,
        "LOAN_TO_VALUE": ltv,
        "INTEREST_RATE": rate,
        "LOAN_AMOUNT": amount,
        "LOAN_TERM": term.astype(float),
        "MONTHLY_PAYMENT": monthly,
        "PREVIOUS_DENIAL_FLAG": rng.choice(["Yes", "No"], n),
        "DEFAULT": y,
    })
    return df

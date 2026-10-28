"""Approval policy: turn default probabilities into APPROVED decisions.

The official Responsible Profit formula is unpublished, so no single profit
assumption is hard-coded. Loan value is evaluated across a documented grid of
plausible scenarios and a threshold is chosen for robustness across them.
"""
import itertools

import numpy as np

# gain if a loan is repaid; loss if it defaults (fraction of principal lost)
GAIN_MODELS = ("interest_total", "interest_one_year")
LGD_GRID = (0.3, 0.5, 0.7, 1.0)


def loan_gain(df, model):
    amount = df["LOAN_AMOUNT"].to_numpy(float)
    if model == "interest_total":
        return np.maximum(df["MONTHLY_PAYMENT"].to_numpy(float) * df["LOAN_TERM"].to_numpy(float) - amount, 0.0)
    if model == "interest_one_year":
        return amount * df["INTEREST_RATE"].to_numpy(float)
    raise ValueError(model)


def scenarios():
    return [{"gain_model": g, "lgd": l} for g, l in itertools.product(GAIN_MODELS, LGD_GRID)]


def realised_profit(df, y, approved, gain_model, lgd):
    """Profit of the approved set on labelled data (sum over approved loans)."""
    gain = loan_gain(df, gain_model)
    loss = lgd * df["LOAN_AMOUNT"].to_numpy(float)
    per_loan = np.where(np.asarray(y) == 1, -loss, gain)
    return float(per_loan[np.asarray(approved).astype(bool)].sum())


def expected_profit_rule(df, p, gain_model, lgd):
    """Approve when (1-p)*gain - p*loss > 0 (needs calibrated p)."""
    gain = loan_gain(df, gain_model)
    loss = lgd * df["LOAN_AMOUNT"].to_numpy(float)
    return ((1 - p) * gain - p * loss) > 0


def threshold_curve(df, y, p, grid=None):
    """Profit of approve-if-p<t for every scenario and threshold."""
    grid = np.linspace(0.02, 0.60, 59) if grid is None else grid
    rows = []
    for sc in scenarios():
        profits = [realised_profit(df, y, p < t, **sc) for t in grid]
        rows.append({**sc, "profit": profits})
    return grid, rows


def robust_threshold(df, y, p, grid=None):
    """Threshold maximising mean profit efficiency across scenarios.

    Efficiency = profit_s(t) / max_t profit_s(t); also report the worst case.
    """
    grid, rows = threshold_curve(df, y, p, grid)
    eff = []
    for r in rows:
        pr = np.array(r["profit"])
        best = pr.max()
        eff.append(pr / best if best > 0 else np.zeros_like(pr))
    eff = np.vstack(eff)
    mean_eff, worst = eff.mean(axis=0), eff.min(axis=0)
    i = int(np.argmax(mean_eff))
    return {
        "threshold": float(grid[i]),
        "mean_efficiency": float(mean_eff[i]),
        "worst_efficiency": float(worst[i]),
        "approval_rate": float((p < grid[i]).mean()),
        "per_scenario": [
            {**{k: r[k] for k in ("gain_model", "lgd")},
             "profit_at_threshold": float(r["profit"][i]),
             "best_profit": float(max(r["profit"])),
             "best_threshold": float(grid[int(np.argmax(r["profit"]))])}
            for r in rows
        ],
    }


def decisions_from_threshold(p, threshold):
    return (np.asarray(p) < threshold).astype(int)

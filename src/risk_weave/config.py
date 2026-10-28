"""Project-wide constants. Decisions here follow instruction-decisions.md and
the approved project plan; change them only with a recorded reason."""

SEED = 20261028
N_FOLDS = 5

ID_COL = "LOAN_ID"
TARGET = "DEFAULT"

# Approved: excluded from the primary model, analysed separately for fairness,
# proxy effects and sensitivity.
SENSITIVE_EXCLUDED = ["RACE_ETH", "GENDER", "AGE_BAND", "AGE_D", "MARITAL_STATUS"]

# Other fields that are plausible proxies of protected attributes. Kept in the
# primary model but evaluated in sensitivity runs (feature set "no_proxy").
PROXY_CANDIDATES = [
    "STATE", "STATE_TIER", "RURAL_URBAN", "PRIMARY_LANGUAGE", "FIRST_GEN_COLLEGE",
    "VETERAN", "COMMUNITY_INVESTMENT_AREA", "PUBLIC_TRANSIT_ACCESS",
    "HISTORIC_ACCESS_SCORE", "WEALTH_GAP_PROXY", "COST_OF_LIVING_INDEX",
    "MEDICAL_DEBT_FLAG", "INSURANCE_COST_TIER", "DEPENDENTS",
]

# Fields whose decision-time availability cannot be confirmed from metadata.
PRICING_FIELD = "INTEREST_RATE"
TIMING_UNCERTAIN = [
    "PREVIOUS_APPROVAL_FLAG", "PREVIOUS_DENIAL_FLAG", "CREDIT_BUILDER_FLAG",
    "CREDIT_MONITORING_FLAG",
]

# Columns needed to value a loan in the policy analysis.
LOAN_VALUE_COLS = ["LOAN_AMOUNT", "INTEREST_RATE", "LOAN_TERM", "MONTHLY_PAYMENT"]

# Group columns used only for fairness reporting, never as primary features.
FAIRNESS_GROUPS = ["RACE_ETH", "GENDER", "AGE_BAND", "MARITAL_STATUS", "STATE_TIER"]


def feature_columns(all_columns, feature_set="primary"):
    """Return model input columns for a named feature set.

    primary          : everything except ID, target and SENSITIVE_EXCLUDED
    no_rate          : primary without INTEREST_RATE
    no_proxy         : primary without PROXY_CANDIDATES
    no_timing        : primary without TIMING_UNCERTAIN
    clean            : primary without INTEREST_RATE, PROXY_CANDIDATES and TIMING_UNCERTAIN
    with_sensitive   : primary plus the sensitive columns (analysis only)
    """
    drop = {ID_COL, TARGET}
    if feature_set != "with_sensitive":
        drop |= set(SENSITIVE_EXCLUDED)
    if feature_set == "no_rate":
        drop.add(PRICING_FIELD)
    elif feature_set == "no_proxy":
        drop |= set(PROXY_CANDIDATES)
    elif feature_set == "no_timing":
        drop |= set(TIMING_UNCERTAIN)
    elif feature_set == "clean":
        drop |= {PRICING_FIELD} | set(PROXY_CANDIDATES) | set(TIMING_UNCERTAIN)
    elif feature_set not in ("primary", "with_sensitive"):
        raise ValueError(f"unknown feature set {feature_set!r}")
    return [c for c in all_columns if c not in drop]

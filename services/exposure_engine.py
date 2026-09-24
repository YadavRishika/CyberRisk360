"""
exposure_engine.py
--------------------
Produces SIMULATED / ESTIMATED financial exposure figures. These are
illustrative order-of-magnitude figures driven by organization size and
current risk posture -- not actuarial calculations, not real quotes.

All amounts are in INR.
"""

SIZE_MULTIPLIER = {
    "Small": 0.6,
    "Medium": 1.0,
    "Large": 1.8,
    "Enterprise": 3.0,
}

# Baseline (illustrative) exposure at a "Medium" org with a mid-range risk
# score, before the risk-score scaling factor is applied.
BASE_EXPOSURE = {
    "ransomware_exposure": 2_500_000,
    "data_breach_exposure": 3_000_000,
    "business_interruption_exposure": 2_000_000,
    "incident_response_exposure": 900_000,
    "regulatory_legal_exposure": 1_200_000,
}


def estimate_exposure(org: dict, signal: dict, risk_score: float) -> dict:
    """
    org: dict with at least 'size_category'
    signal: dict with security_incidents, avg_remediation_days
    risk_score: current computed risk score (0-100)

    Scaling logic (documented, not hidden):
      - Base exposure per category is scaled by an org-size multiplier.
      - Then scaled again by a risk factor = 0.5 + (risk_score / 100)
        i.e. a risk score of 0 halves the base exposure, a risk score of
        100 multiplies it by 1.5 -- reflecting that a worse security
        posture raises the plausible cost of an incident.
      - Incident response exposure additionally scales with the number of
        recent security incidents (more incidents => higher expected
        response cost).
    """
    size_mult = SIZE_MULTIPLIER.get(org.get("size_category", "Medium"), 1.0)
    risk_factor = 0.5 + (risk_score / 100.0)

    incidents = signal.get("security_incidents", 0)
    incident_mult = 1.0 + (0.15 * incidents)

    exposure = {}
    for category, base in BASE_EXPOSURE.items():
        value = base * size_mult * risk_factor
        if category == "incident_response_exposure":
            value *= incident_mult
        exposure[category] = round(value, -3)  # round to nearest thousand

    exposure["calculation_basis"] = "SIMULATED"
    return exposure

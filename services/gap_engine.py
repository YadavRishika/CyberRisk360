"""
gap_engine.py
---------------
Compares simulated financial exposure against existing (simulated) policy
coverage limits and flags gaps. Produces review recommendations only --
never a premium figure, never an automatic coverage change.
"""

# Maps exposure_engine categories -> Coverage.coverage_type enum values
EXPOSURE_TO_COVERAGE_TYPE = {
    "ransomware_exposure": "Ransomware",
    "data_breach_exposure": "Data Breach",
    "business_interruption_exposure": "Business Interruption",
    "incident_response_exposure": "Incident Response",
    "regulatory_legal_exposure": "Third-Party Liability",
}


def detect_gaps(exposure: dict, coverages: list) -> list:
    """
    exposure: dict from exposure_engine.estimate_exposure()
    coverages: list of dicts, each with 'coverage_type' and 'coverage_limit'

    Returns a list of gap dicts, one per exposure category:
        {
          "category": "Ransomware",
          "estimated_exposure": 4500000,
          "existing_coverage": 2500000,
          "gap_amount": 2000000,
          "gap_pct": 44.4,
          "gap_detected": True,
          "recommendation": "Coverage gap detected ..."
        }
    """
    coverage_by_type = {c["coverage_type"]: c["coverage_limit"] for c in coverages}

    results = []
    for exposure_key, coverage_type in EXPOSURE_TO_COVERAGE_TYPE.items():
        est = exposure.get(exposure_key, 0)
        limit = coverage_by_type.get(coverage_type, 0)
        gap_amount = max(0, est - limit)
        gap_pct = round((gap_amount / est) * 100, 1) if est > 0 else 0.0
        gap_detected = gap_amount > 0

        if gap_detected:
            recommendation = (
                f"Coverage gap detected in {coverage_type}. "
                f"Analyst review recommended -- estimated exposure exceeds "
                f"existing coverage limit by roughly \u20b9{gap_amount:,.0f}."
            )
        else:
            recommendation = f"{coverage_type} coverage currently appears adequate for estimated exposure."

        results.append({
            "category": coverage_type,
            "estimated_exposure": est,
            "existing_coverage": limit,
            "gap_amount": gap_amount,
            "gap_pct": gap_pct,
            "gap_detected": gap_detected,
            "recommendation": recommendation,
        })

    return results

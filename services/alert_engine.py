"""
alert_engine.py
------------------
Decides whether a Risk Alert should be raised, and builds its explainable
content. Never sets a status other than "Pending Analyst Review" -- only a
human analyst can change that.
"""


def should_raise_alert(delta: float, gaps: list, threshold: float) -> bool:
    any_gap = any(g["gap_detected"] for g in gaps)
    return delta >= threshold or any_gap


def build_alert_payload(explanation: dict, gaps: list) -> dict:
    """
    explanation: output of risk_engine.explain_change()
    gaps: output of gap_engine.detect_gaps()

    Returns the fields needed to create a RiskAlert row.
    """
    if explanation["main_contributors"]:
        top = explanation["main_contributors"][0]
        main_reason = (
            f"{top['factor']} {top['direction']} "
            f"(contributing {top['point_change']:+.1f} points to the risk score). "
            + explanation["headline"]
        )
    else:
        main_reason = explanation["headline"]

    flagged_gaps = [g for g in gaps if g["gap_detected"]]
    if flagged_gaps:
        gap_lines = [
            f"{g['category']}: \u20b9{g['gap_amount']:,.0f} gap "
            f"({g['gap_pct']}% of estimated exposure uncovered)"
            for g in flagged_gaps
        ]
        coverage_gap_summary = "; ".join(gap_lines)
        recommendation = (
            "Review the following coverage categories with an analyst: "
            + ", ".join(g["category"] for g in flagged_gaps)
            + ". " + explanation["recommended_action"]
        )
    else:
        coverage_gap_summary = "No coverage gaps detected at current exposure levels."
        recommendation = explanation["recommended_action"]

    return {
        "previous_score": explanation["previous_score"],
        "current_score": explanation["current_score"],
        "main_reason": main_reason,
        "coverage_gap_summary": coverage_gap_summary,
        "recommendation": recommendation,
        "status": "Pending Analyst Review",
    }

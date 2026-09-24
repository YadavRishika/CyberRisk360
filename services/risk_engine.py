"""
risk_engine.py
----------------
A deliberately transparent (non-black-box) risk scoring engine.

Every sub-score is a simple, documented formula. Every final score carries
a full breakdown so an analyst can see exactly how it was produced and
exactly what changed between two assessments.
"""

WEIGHTS = {
    "vulnerability_risk": 0.30,
    "mfa_risk": 0.20,
    "incident_risk": 0.20,
    "backup_risk": 0.15,
    "patch_risk": 0.15,
}

FACTOR_LABELS = {
    "vulnerability_risk": "Critical vulnerabilities",
    "mfa_risk": "MFA coverage",
    "incident_risk": "Security incidents",
    "backup_risk": "Backup compliance",
    "patch_risk": "Patch compliance",
}


def _clamp(value, low=0, high=100):
    return max(low, min(high, value))


def calculate_risk_score(signal: dict) -> dict:
    """
    signal: dict with keys critical_vulnerabilities, mfa_coverage_pct,
    security_incidents, backup_compliance_pct, patch_compliance_pct
    (endpoint_protection_pct / training_compliance_pct / avg_remediation_days
    are stored and displayed but not part of the scoring formula below --
    kept simple and documented on purpose; see README for extension notes).

    Returns a dict:
        {
          "risk_score": float (0-100),
          "risk_band": "Low"|"Medium"|"High"|"Critical",
          "breakdown": {
              factor_key: {
                  "label": str,
                  "raw_risk": float (0-100, before weighting),
                  "weight": float,
                  "weighted_points": float,
              }, ...
          }
        }
    """
    vulnerability_risk = _clamp(signal["critical_vulnerabilities"] * 10)
    mfa_risk = _clamp(100 - signal["mfa_coverage_pct"])
    incident_risk = _clamp(signal["security_incidents"] * 25)
    backup_risk = _clamp(100 - signal["backup_compliance_pct"])
    patch_risk = _clamp(100 - signal["patch_compliance_pct"])

    raw = {
        "vulnerability_risk": vulnerability_risk,
        "mfa_risk": mfa_risk,
        "incident_risk": incident_risk,
        "backup_risk": backup_risk,
        "patch_risk": patch_risk,
    }

    breakdown = {}
    total = 0.0
    for key, raw_value in raw.items():
        weight = WEIGHTS[key]
        weighted_points = round(raw_value * weight, 2)
        total += weighted_points
        breakdown[key] = {
            "label": FACTOR_LABELS[key],
            "raw_risk": round(raw_value, 2),
            "weight": weight,
            "weighted_points": weighted_points,
        }

    total = round(_clamp(total), 2)

    if total < 30:
        band = "Low"
    elif total < 55:
        band = "Medium"
    elif total < 75:
        band = "High"
    else:
        band = "Critical"

    return {"risk_score": total, "risk_band": band, "breakdown": breakdown}


def explain_change(previous: dict, current: dict) -> dict:
    """
    previous / current: the dicts returned by calculate_risk_score(), or
    None for `previous` if this is the organization's first assessment.

    Returns an explanation payload used both by the alert generator and the
    dashboard's "why did this change" panel.
    """
    curr_score = current["risk_score"]
    prev_score = previous["risk_score"] if previous else curr_score
    delta = round(curr_score - prev_score, 2)

    contributors = []
    for key, curr_factor in current["breakdown"].items():
        prev_points = previous["breakdown"][key]["weighted_points"] if previous else curr_factor["weighted_points"]
        point_change = round(curr_factor["weighted_points"] - prev_points, 2)
        if point_change != 0:
            contributors.append({
                "factor": curr_factor["label"],
                "point_change": point_change,
                "direction": "increased risk" if point_change > 0 else "decreased risk",
            })

    # Largest absolute contributors first
    contributors.sort(key=lambda c: abs(c["point_change"]), reverse=True)

    if delta > 0:
        headline = f"Risk increased: {prev_score} \u2192 {curr_score} (+{delta})"
    elif delta < 0:
        headline = f"Risk decreased: {prev_score} \u2192 {curr_score} ({delta})"
    else:
        headline = f"Risk unchanged at {curr_score}"

    if current["risk_band"] in ("High", "Critical") and delta >= 0:
        recommended_action = (
            "Escalate for analyst review of current coverage adequacy, "
            "particularly ransomware and business interruption coverage."
        )
    elif delta > 0:
        recommended_action = "Monitor next signal cycle; review if the upward trend continues."
    else:
        recommended_action = "No immediate action required; continue routine monitoring."

    return {
        "headline": headline,
        "previous_score": prev_score,
        "current_score": curr_score,
        "delta": delta,
        "risk_band": current["risk_band"],
        "main_contributors": contributors[:4],
        "recommended_action": recommended_action,
    }

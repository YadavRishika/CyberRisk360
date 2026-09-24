# CyberRisk360 — Sample Test Cases

| # | Module | Test Case | Input (summary) | Expected Result | Type |
|---|--------|-----------|------------------|------------------|------|
| TC-01 | Risk Engine | Risk score computed correctly for a healthy posture | CritVuln=2, MFA=90%, Incidents=0, Backup=95%, Patch=92% | Score ≈ 9–12, band = Low | Unit |
| TC-02 | Risk Engine | Risk score rises correctly for a degraded posture | CritVuln=7, MFA=65%, Incidents=2, Backup=80%, Patch=72% | Score ≈ 40–50, band = Medium | Unit |
| TC-03 | Risk Engine | Weights sum to 1.0 and formula is deterministic | Any valid signal | Same input always produces same score/breakdown | Unit |
| TC-04 | Risk Engine | Explanation attributes the correct top contributor | Signal where only critical_vulnerabilities changed | `main_contributors[0].factor == "Critical vulnerabilities"` | Unit |
| TC-05 | Risk Engine | First-ever assessment (no previous) handled gracefully | previous = None | `delta == 0`, no crash, headline states score unchanged | Edge case |
| TC-06 | Exposure Engine | Larger org size increases exposure proportionally | Same signal, size="Small" vs "Enterprise" | Enterprise exposure > Small exposure, ratio ≈ 3.0/0.6 | Unit |
| TC-07 | Exposure Engine | Higher risk score increases exposure | Same signal, risk_score=20 vs risk_score=90 | Exposure at 90 > exposure at 20 | Unit |
| TC-08 | Gap Engine | Gap correctly detected when exposure > coverage limit | exposure=4,000,000; limit=2,500,000 | `gap_detected=True`, `gap_amount=1,500,000` | Unit |
| TC-09 | Gap Engine | No gap when coverage is sufficient | exposure=1,800,000; limit=2,500,000 | `gap_detected=False`, `gap_amount=0` | Unit |
| TC-10 | Alert Engine | Alert raised when score increase ≥ threshold | delta=12, threshold=8, no gaps | `should_raise_alert=True` | Unit |
| TC-11 | Alert Engine | Alert raised due to coverage gap even if score is flat | delta=0, one gap detected | `should_raise_alert=True` | Unit |
| TC-12 | Alert Engine | No alert when risk stable and no gaps | delta=1, threshold=8, no gaps | `should_raise_alert=False` | Unit |
| TC-13 | API | GET /api/dashboard/<org_id> for valid org | org_id=1 (seeded) | HTTP 200, JSON includes trend, explanation, gaps, alerts, disclaimer | Integration |
| TC-14 | API | GET /api/dashboard/<org_id> for non-existent org | org_id=999 | HTTP 404 | Integration |
| TC-15 | API | POST /api/alerts/<id>/review without analyst_name | `{"decision": "Approve"}` | HTTP 400, error message | Integration |
| TC-16 | API | POST /api/alerts/<id>/review with valid Approve decision | `{"analyst_name": "R. Sharma", "decision": "Approve", "comments": "..."}` | HTTP 200, alert.status == "Approved", review + history row created | Integration |
| TC-17 | API | POST /api/alerts/<id>/review with invalid decision value | `{"decision": "Bind Policy"}` | HTTP 400, rejected — system never accepts a binding action | Integration / Security constraint |
| TC-18 | API | POST /api/simulate/<org_id> with direction="worsen" | org_id=1 | New signal created with degraded values, new assessment + possibly new alert | Integration |
| TC-19 | Workflow | Full lifecycle: signal → score → explanation → exposure → gap → alert → review → history | Seeded dataset, then one simulate + one review call | All 8 pipeline stages produce a persisted record, history shows both "Alert Generated" and "Analyst decision" entries | End-to-end |
| TC-20 | Constraint check | System never writes a premium value anywhere | Inspect all API responses / DB columns | No field named premium/bound_amount exists; only exposure & coverage-limit fields | Compliance/negative test |

## Notes for running these as automated tests
Unit tests (TC-01 to TC-12) can run directly against `services/*.py` with no
database, using plain Python dicts (see the verification script used during
development, reproducible with `pytest` by wrapping the same assertions).
Integration tests (TC-13 to TC-19) require a running MySQL instance seeded
via `seed_data.py`, and can be exercised with `pytest` + `requests` or
Flask's test client (`app.test_client()`).

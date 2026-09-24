# Demo Scenario — for presentation / viva

Suggested run order (10–12 minutes):

**1. Open the dashboard (30 sec)**
Show the masthead, account selector, and point out the disclaimer bar —
lead with the "this is a decision-support tool, not an underwriting
engine" framing before anything else, so the scope is clear immediately.

**2. Walk the case summary for "BrightHealth Diagnostics" (1 min)**
This org has the worst trend in the seed data. Show:
- Current risk score + band
- The trend chart climbing from Jan → May, dipping slightly in June
- Point out this is exactly the "periodic snapshot vs continuous signal"
  problem from the original brief — a once-a-year audit would have missed
  the March–May spike entirely.

**3. Explain the "why" panel (2 min)**
- Read the headline (e.g. "Risk increased: 61.4 → 74.8 (+13.4)")
- Walk the contributors table: which factor moved the score the most and
  why (critical vulnerabilities and MFA coverage typically dominate)
- Show the bar chart — visually the same data, easier to scan
- This is the core "explainability" requirement from faculty feedback.

**4. Financial exposure & coverage gap table (2 min)**
- Point out every figure is simulated
- Show the Incident Response or Ransomware row with a detected gap
- Explain the formula in one sentence: exposure scales with org size and
  current risk score, gap = exposure − existing limit
- Emphasize: no premium number appears anywhere on this page.

**5. Trigger a live "what-if" (2 min)**
- Click "Simulate decline" — a new monthly snapshot is generated with
  randomly worsened signals
- Show the dashboard refresh: new score, new explanation, possibly a new
  alert card appearing with status "Pending Analyst Review"
- This demonstrates the "continuous/dynamic" requirement live.

**6. Analyst review workflow (2 min)**
- Click "Review" on a pending alert
- Fill in analyst name + comments, click Approve (or Request Info to show
  that path too)
- Show the alert card status badge change color/label
- Scroll to Review History table — show the new row was appended, and
  that the original "Alert Generated" system entry is still there too.
- This demonstrates human-in-the-loop control and full audit trail.

**7. Guidewire ecosystem framing (1 min)**
- Briefly show the conceptual integration diagram from the documentation
  (Cyber Risk Analytics → Policy/Coverage Review → Analyst Decision →
  Insurance System) and explain this project outputs structured data that
  *could* feed PolicyCenter's coverage review process, without directly
  integrating with or modifying Guidewire's proprietary systems.

**8. Close on limitations (30 sec)**
State explicitly: simulated data, linear/transparent (not ML-validated)
scoring, illustrative exposure figures, no binding/pricing anywhere in the
system, always subject to analyst sign-off.

## Suggested talking point if asked "why not use real data / real ML?"
Explain this was a deliberate scoping decision based directly on faculty
feedback: continuous real cyber telemetry requires data-sharing agreements
and consent frameworks the organization doesn't have; an unvalidated ML
risk model risks false precision; and any system that could set premiums
or bind coverage crosses into regulated insurance territory. The project
demonstrates the analytics and workflow pattern end-to-end on simulated
data so the architecture is provably sound before those harder problems
are tackled in a production context.

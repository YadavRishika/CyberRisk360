# CyberRisk360
### Guidewire-Oriented Cyber Risk Analytics & Insurance Review Accelerator

A decision-support platform that turns simulated, time-varying cybersecurity
signals into an explainable risk score, a simulated financial exposure
estimate, a coverage-gap analysis, and a human-analyst review workflow.
**It does not bind policies, set premiums, or make final insurance
decisions** — every recommendation ends with an analyst approving,
rejecting, or requesting more information.

---

## 1. Project structure

```
project/
├── app.py                     # Flask entry point, creates the app
├── config.py                  # DB connection + tunables (thresholds, disclaimer text)
├── seed_data.py                # Loads sample CSVs, runs pipeline over history
├── requirements.txt
├── schema.sql                  # Run this first to create the MySQL database
├── sample_security_signals.csv # Simulated signal time series (3 orgs, 6 months)
├── sample_policy_coverage.csv  # Simulated policies + coverage limits
├── models/__init__.py          # SQLAlchemy ORM models (9 tables)
├── services/
│   ├── risk_engine.py          # Explainable weighted risk scoring
│   ├── exposure_engine.py      # Simulated financial exposure estimation
│   ├── gap_engine.py           # Exposure vs coverage gap detection
│   └── alert_engine.py         # Alert trigger logic + payload builder
├── routes/api.py               # All REST endpoints + pipeline orchestration
├── templates/dashboard.html    # Single-page analyst dashboard
├── static/css/style.css        # "Risk ledger" visual design
├── static/js/dashboard.js      # Fetches API data, renders Chart.js + tables
├── TEST_CASES.md
└── DEMO_SCENARIO.md
```

---

## 2. First-time setup

### Prerequisites
- Python 3.10+
- MySQL Server 8.0+ (running locally, or reachable over network)
- pip

### Steps

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database and tables
mysql -u root -p < schema.sql

# 4. Point the app at your MySQL instance
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_NAME=cyberrisk360
# (Windows PowerShell: use  $env:DB_HOST="localhost"  etc.)

# 5. Load the simulated sample dataset and run the risk pipeline over it
python seed_data.py

# 6. Run the app
python app.py
```

Open **http://localhost:5000** — you should see three seeded organizations
in the account selector, each with 6 months of history and at least one
generated alert.

### If you don't have MySQL installed yet
Any of these work: install MySQL Community Server directly, use XAMPP/WAMP
(bundles MySQL with a GUI), or run it in Docker:
```bash
docker run --name cyberrisk-mysql -e MYSQL_ROOT_PASSWORD=yourpassword -p 3306:3306 -d mysql:8.0
```
Then continue from step 3 above.

---

## 3. How the pieces fit together (read this before modifying code)

The **pipeline** (`run_assessment_pipeline` in `routes/api.py`) is the spine
of the whole system and runs in this order every time a new signal snapshot
appears (either from seeding or from the "Simulate" button):

```
SecuritySignal (row)
   → risk_engine.calculate_risk_score()      → RiskAssessment (row)
   → risk_engine.explain_change()            → explanation dict (not stored, computed on read too)
   → exposure_engine.estimate_exposure()     → FinancialExposure (row)
   → gap_engine.detect_gaps()                → gap list (not stored, computed on read)
   → alert_engine.should_raise_alert() / build_alert_payload()
        → if triggered: RiskAlert (row) + ReviewHistory (row)
```

Notice that **explanations and gaps are recomputed on every read**, not
stored — this keeps them always consistent with the latest formulas, and
is a deliberate design choice worth mentioning in your viva.

The **analyst review workflow** is the only place `RiskAlert.status`
changes. `POST /api/alerts/<id>/review` is intentionally the single write
path for a decision, and it always requires `analyst_name` — there's no
endpoint anywhere that flips an alert to "Approved" automatically.

---

## 4. Common ways you'll want to extend this for your report/demo

**Add a new signal type** (e.g. cloud misconfigurations):
1. Add the column to `security_signal` in `schema.sql` and `models/__init__.py`.
2. Add it to `_signal_to_score_input()` in `routes/api.py` if it should
   affect scoring, and give it a weight in `services/risk_engine.py`
   (remember to keep all weights summing to 1.0).
3. Add it to the sample CSV and to the signal table render in `dashboard.js`.

**Add a new coverage category:**
1. Add the value to the `coverage_type` ENUM in `schema.sql` (and re-create
   the table, or `ALTER TABLE` if you already have data).
2. Add a matching entry to `EXPOSURE_TO_COVERAGE_TYPE` in `gap_engine.py`
   and a base exposure figure in `exposure_engine.py`.

**Change the alert sensitivity:**
Edit `RISK_INCREASE_ALERT_THRESHOLD` in `config.py`.

**Add authentication for analysts:**
Currently `analyst_name` is free text for demo simplicity. For a more
complete submission, add a simple `Analyst` table + session-based login and
swap the free-text field in the review modal for a logged-in user's name.

**Swap in scikit-learn (optional, per the brief):**
A natural, low-risk addition: use `sklearn.linear_model.LinearRegression`
or an isotonic fit to *validate* that your hand-set weights correlate with
a synthetic "ground truth" severity label you generate — and present that
as a transparency/validation appendix, not as a replacement for the
explainable formula. Keep the scoring formula itself simple and readable;
that's the whole point of the "no black box" requirement.

---

## 5. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Can't connect to MySQL server` | MySQL not running, or wrong host/port | Confirm `mysql -u root -p` works standalone first |
| `Access denied for user` | Wrong `DB_USER`/`DB_PASSWORD` | Re-check env vars in the same shell you run `python app.py` from |
| Dashboard loads but dropdown is empty | `seed_data.py` wasn't run, or ran against a different DB | Re-run `python seed_data.py`, check `DB_NAME` matches `schema.sql` |
| `Table doesn't exist` errors | `schema.sql` wasn't applied | Re-run `mysql -u root -p < schema.sql` |
| Charts don't render | No internet access to cdnjs.cloudflare.com (Chart.js CDN) | Download `chart.umd.min.js` locally and update the `<script src>` in `dashboard.html` |
| "Simulate" button does nothing | Check browser console; likely a 400/500 from `/api/simulate/<id>` | Confirm the org has at least one signal already (seed data must have run) |

---

## 6. Suggested order to present this for your project report

1. Problem statement + faculty feedback (show you addressed every point)
2. Architecture diagram
3. ER diagram + schema.sql
4. Risk-scoring methodology (walk the formula on paper first, then show
   `risk_engine.py`)
5. Live demo using `DEMO_SCENARIO.md`
6. Test cases table (`TEST_CASES.md`)
7. Limitations slide (be upfront — this is what turns "unreliable scope"
   into "responsibly scoped")
8. Guidewire ecosystem integration diagram
9. Future enhancements

---

## 7. Explicit scope boundaries (keep repeating these in your report)

- All signals, scores, exposure figures, and policy/coverage data are
  **simulated**.
- The system **never** computes a real insurance premium.
- The system **never** automatically binds, approves, or issues a policy.
- Every recommendation requires a named analyst's explicit decision before
  it has any effect on alert status.
- The risk-scoring model is a transparent weighted formula, not a
  validated actuarial or ML model — treat its output as a **screening
  signal for review prioritization**, not a certified risk rating.

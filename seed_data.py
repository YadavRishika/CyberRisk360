"""
seed_data.py
--------------
Populates the MySQL database with the simulated sample dataset and runs
the full risk pipeline (score -> explanation -> exposure -> gaps -> alerts)
over each historical snapshot, so the dashboard has a trend line and at
least one alert to review out of the box.

Run once after creating the schema:
    python seed_data.py
"""
import csv
from datetime import datetime

from app import create_app
from models import db, Organization, SecuritySignal, Policy, Coverage
from routes.api import run_assessment_pipeline

ORG_PROFILE = {
    "Nimbus Retail Pvt Ltd": {"industry": "Retail", "size_category": "Medium", "employee_count": 420, "annual_revenue": 180_000_000},
    "Vertex Logistics Ltd": {"industry": "Logistics", "size_category": "Large", "employee_count": 1200, "annual_revenue": 650_000_000},
    "BrightHealth Diagnostics": {"industry": "Healthcare", "size_category": "Medium", "employee_count": 300, "annual_revenue": 120_000_000},
}


def load_organizations_and_signals(path="sample_security_signals.csv"):
    orgs_by_name = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        name = row["org_name"]
        if name not in orgs_by_name:
            profile = ORG_PROFILE.get(name, {"industry": "Other", "size_category": "Medium", "employee_count": 200, "annual_revenue": 50_000_000})
            org = Organization(name=name, **profile)
            db.session.add(org)
            db.session.flush()
            orgs_by_name[name] = org

    db.session.commit()

    signals = []
    for row in rows:
        org = orgs_by_name[row["org_name"]]
        signal = SecuritySignal(
            org_id=org.org_id,
            snapshot_date=datetime.strptime(row["snapshot_date"], "%Y-%m-%d").date(),
            critical_vulnerabilities=int(row["critical_vulnerabilities"]),
            patch_compliance_pct=float(row["patch_compliance_pct"]),
            mfa_coverage_pct=float(row["mfa_coverage_pct"]),
            security_incidents=int(row["security_incidents"]),
            backup_compliance_pct=float(row["backup_compliance_pct"]),
            endpoint_protection_pct=float(row["endpoint_protection_pct"]),
            training_compliance_pct=float(row["training_compliance_pct"]),
            avg_remediation_days=float(row["avg_remediation_days"]),
        )
        db.session.add(signal)
        signals.append(signal)
    db.session.commit()

    return orgs_by_name, signals


def load_policies_and_coverage(orgs_by_name, path="sample_policy_coverage.csv"):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    policies_by_number = {}
    for row in rows:
        org = orgs_by_name[row["org_name"]]
        pol_number = row["policy_number"]
        if pol_number not in policies_by_number:
            policy = Policy(
                org_id=org.org_id,
                policy_number=pol_number,
                effective_date=datetime.strptime(row["effective_date"], "%Y-%m-%d").date(),
                expiry_date=datetime.strptime(row["expiry_date"], "%Y-%m-%d").date(),
                status=row["status"],
            )
            db.session.add(policy)
            db.session.flush()
            policies_by_number[pol_number] = policy

        db.session.add(Coverage(
            policy_id=policies_by_number[pol_number].policy_id,
            coverage_type=row["coverage_type"],
            coverage_limit=float(row["coverage_limit_inr"]),
            deductible=float(row["deductible_inr"]),
        ))

    db.session.commit()


def run_pipeline_over_history(orgs_by_name, signals):
    signals_sorted = sorted(signals, key=lambda s: (s.org_id, s.snapshot_date))
    for signal in signals_sorted:
        org = Organization.query.get(signal.org_id)
        run_assessment_pipeline(org, signal)


def main():
    app = create_app()
    with app.app_context():
        print("Creating tables (if not already present)...")
        db.create_all()

        print("Clearing existing data for a clean seed...")
        # Delete in FK-safe order
        from models import ReviewHistory, AnalystReview, RiskAlert, FinancialExposure, RiskAssessment, SecuritySignal, Coverage, Policy, Organization
        for model in [ReviewHistory, AnalystReview, RiskAlert, FinancialExposure, RiskAssessment, SecuritySignal, Coverage, Policy, Organization]:
            model.query.delete()
        db.session.commit()

        print("Loading organizations and security signals...")
        orgs_by_name, signals = load_organizations_and_signals()

        print("Loading policies and coverage...")
        load_policies_and_coverage(orgs_by_name)

        print("Running risk pipeline across historical snapshots (this generates assessments, exposure, gaps, and alerts)...")
        run_pipeline_over_history(orgs_by_name, signals)

        print("Seed complete.")
        print(f"Organizations: {Organization.query.count()}")
        print(f"Signals: {SecuritySignal.query.count()}")
        from models import RiskAssessment as RA, RiskAlert as RL
        print(f"Assessments: {RA.query.count()}")
        print(f"Alerts generated: {RL.query.count()}")


if __name__ == "__main__":
    main()

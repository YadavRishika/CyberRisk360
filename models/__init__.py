from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Organization(db.Model):
    __tablename__ = "organization"
    org_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100))
    size_category = db.Column(db.Enum("Small", "Medium", "Large", "Enterprise"), nullable=False)
    employee_count = db.Column(db.Integer)
    annual_revenue = db.Column(db.Numeric(18, 2))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "org_id": self.org_id,
            "name": self.name,
            "industry": self.industry,
            "size_category": self.size_category,
            "employee_count": self.employee_count,
            "annual_revenue": float(self.annual_revenue) if self.annual_revenue is not None else None,
        }


class SecuritySignal(db.Model):
    __tablename__ = "security_signal"
    signal_id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organization.org_id"), nullable=False)
    snapshot_date = db.Column(db.Date, nullable=False)
    critical_vulnerabilities = db.Column(db.Integer, default=0)
    patch_compliance_pct = db.Column(db.Numeric(5, 2), default=100)
    mfa_coverage_pct = db.Column(db.Numeric(5, 2), default=100)
    security_incidents = db.Column(db.Integer, default=0)
    backup_compliance_pct = db.Column(db.Numeric(5, 2), default=100)
    endpoint_protection_pct = db.Column(db.Numeric(5, 2), default=100)
    training_compliance_pct = db.Column(db.Numeric(5, 2), default=100)
    avg_remediation_days = db.Column(db.Numeric(6, 2), default=0)

    def to_dict(self):
        return {
            "signal_id": self.signal_id,
            "org_id": self.org_id,
            "snapshot_date": self.snapshot_date.isoformat(),
            "critical_vulnerabilities": self.critical_vulnerabilities,
            "patch_compliance_pct": float(self.patch_compliance_pct),
            "mfa_coverage_pct": float(self.mfa_coverage_pct),
            "security_incidents": self.security_incidents,
            "backup_compliance_pct": float(self.backup_compliance_pct),
            "endpoint_protection_pct": float(self.endpoint_protection_pct),
            "training_compliance_pct": float(self.training_compliance_pct),
            "avg_remediation_days": float(self.avg_remediation_days),
        }


class RiskAssessment(db.Model):
    __tablename__ = "risk_assessment"
    assessment_id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organization.org_id"), nullable=False)
    signal_id = db.Column(db.Integer, db.ForeignKey("security_signal.signal_id"), nullable=False)
    assessment_date = db.Column(db.Date, nullable=False)
    risk_score = db.Column(db.Numeric(5, 2), nullable=False)
    risk_band = db.Column(db.Enum("Low", "Medium", "High", "Critical"), nullable=False)
    score_breakdown = db.Column(db.JSON)

    def to_dict(self):
        return {
            "assessment_id": self.assessment_id,
            "org_id": self.org_id,
            "signal_id": self.signal_id,
            "assessment_date": self.assessment_date.isoformat(),
            "risk_score": float(self.risk_score),
            "risk_band": self.risk_band,
            "score_breakdown": self.score_breakdown,
        }


class FinancialExposure(db.Model):
    __tablename__ = "financial_exposure"
    exposure_id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organization.org_id"), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey("risk_assessment.assessment_id"), nullable=False)
    ransomware_exposure = db.Column(db.Numeric(18, 2), default=0)
    data_breach_exposure = db.Column(db.Numeric(18, 2), default=0)
    business_interruption_exposure = db.Column(db.Numeric(18, 2), default=0)
    incident_response_exposure = db.Column(db.Numeric(18, 2), default=0)
    regulatory_legal_exposure = db.Column(db.Numeric(18, 2), default=0)
    calculation_basis = db.Column(db.String(50), default="SIMULATED")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "exposure_id": self.exposure_id,
            "org_id": self.org_id,
            "assessment_id": self.assessment_id,
            "ransomware_exposure": float(self.ransomware_exposure),
            "data_breach_exposure": float(self.data_breach_exposure),
            "business_interruption_exposure": float(self.business_interruption_exposure),
            "incident_response_exposure": float(self.incident_response_exposure),
            "regulatory_legal_exposure": float(self.regulatory_legal_exposure),
            "calculation_basis": self.calculation_basis,
        }


class Policy(db.Model):
    __tablename__ = "policy"
    policy_id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organization.org_id"), nullable=False)
    policy_number = db.Column(db.String(50), unique=True, nullable=False)
    effective_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    status = db.Column(db.Enum("Active", "Expired", "Under Review"), default="Active")
    coverages = db.relationship("Coverage", backref="policy", lazy=True)

    def to_dict(self):
        return {
            "policy_id": self.policy_id,
            "org_id": self.org_id,
            "policy_number": self.policy_number,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "status": self.status,
            "coverages": [c.to_dict() for c in self.coverages],
        }


class Coverage(db.Model):
    __tablename__ = "coverage"
    coverage_id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey("policy.policy_id"), nullable=False)
    coverage_type = db.Column(
        db.Enum("Ransomware", "Data Breach", "Business Interruption",
                "Incident Response", "Third-Party Liability"),
        nullable=False,
    )
    coverage_limit = db.Column(db.Numeric(18, 2), nullable=False)
    deductible = db.Column(db.Numeric(18, 2), default=0)

    def to_dict(self):
        return {
            "coverage_id": self.coverage_id,
            "policy_id": self.policy_id,
            "coverage_type": self.coverage_type,
            "coverage_limit": float(self.coverage_limit),
            "deductible": float(self.deductible),
        }


class RiskAlert(db.Model):
    __tablename__ = "risk_alert"
    alert_id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organization.org_id"), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey("risk_assessment.assessment_id"), nullable=False)
    exposure_id = db.Column(db.Integer, db.ForeignKey("financial_exposure.exposure_id"))
    previous_score = db.Column(db.Numeric(5, 2))
    current_score = db.Column(db.Numeric(5, 2))
    main_reason = db.Column(db.Text)
    coverage_gap_summary = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    status = db.Column(
        db.Enum("Pending Analyst Review", "Approved", "Rejected", "Info Requested"),
        default="Pending Analyst Review",
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    reviews = db.relationship("AnalystReview", backref="alert", lazy=True)
    history = db.relationship("ReviewHistory", backref="alert", lazy=True)

    def to_dict(self):
        return {
            "alert_id": self.alert_id,
            "org_id": self.org_id,
            "assessment_id": self.assessment_id,
            "exposure_id": self.exposure_id,
            "previous_score": float(self.previous_score) if self.previous_score is not None else None,
            "current_score": float(self.current_score) if self.current_score is not None else None,
            "main_reason": self.main_reason,
            "coverage_gap_summary": self.coverage_gap_summary,
            "recommendation": self.recommendation,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AnalystReview(db.Model):
    __tablename__ = "analyst_review"
    review_id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("risk_alert.alert_id"), nullable=False)
    analyst_name = db.Column(db.String(100), nullable=False)
    decision = db.Column(db.Enum("Approve", "Reject", "Request Info"), nullable=False)
    comments = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "review_id": self.review_id,
            "alert_id": self.alert_id,
            "analyst_name": self.analyst_name,
            "decision": self.decision,
            "comments": self.comments,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }


class ReviewHistory(db.Model):
    __tablename__ = "review_history"
    history_id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("risk_alert.alert_id"), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    action_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "history_id": self.history_id,
            "alert_id": self.alert_id,
            "action": self.action,
            "notes": self.notes,
            "action_at": self.action_at.isoformat() if self.action_at else None,
        }

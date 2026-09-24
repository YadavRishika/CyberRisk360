-- =====================================================================
-- CyberRisk360: Guidewire-Oriented Cyber Risk Analytics & Insurance
-- Review Accelerator — MySQL Schema
-- NOTE: All data populated via this schema in the demo is SIMULATED.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS cyberrisk360;
USE cyberrisk360;

-- ---------------------------------------------------------------------
-- Organization / Account
-- ---------------------------------------------------------------------
CREATE TABLE organization (
    org_id            INT AUTO_INCREMENT PRIMARY KEY,
    name              VARCHAR(150) NOT NULL,
    industry          VARCHAR(100),
    size_category     ENUM('Small','Medium','Large','Enterprise') NOT NULL,
    employee_count     INT,
    annual_revenue    DECIMAL(18,2) COMMENT 'Simulated figure',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- Security Signal (time-varying simulated telemetry)
-- ---------------------------------------------------------------------
CREATE TABLE security_signal (
    signal_id                  INT AUTO_INCREMENT PRIMARY KEY,
    org_id                     INT NOT NULL,
    snapshot_date              DATE NOT NULL,
    critical_vulnerabilities   INT DEFAULT 0,
    patch_compliance_pct       DECIMAL(5,2) DEFAULT 100.00,
    mfa_coverage_pct           DECIMAL(5,2) DEFAULT 100.00,
    security_incidents         INT DEFAULT 0,
    backup_compliance_pct      DECIMAL(5,2) DEFAULT 100.00,
    endpoint_protection_pct    DECIMAL(5,2) DEFAULT 100.00,
    training_compliance_pct    DECIMAL(5,2) DEFAULT 100.00,
    avg_remediation_days       DECIMAL(6,2) DEFAULT 0.00,
    FOREIGN KEY (org_id) REFERENCES organization(org_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Risk Assessment (computed, explainable)
-- ---------------------------------------------------------------------
CREATE TABLE risk_assessment (
    assessment_id       INT AUTO_INCREMENT PRIMARY KEY,
    org_id               INT NOT NULL,
    signal_id            INT NOT NULL,
    assessment_date      DATE NOT NULL,
    risk_score           DECIMAL(5,2) NOT NULL,
    risk_band            ENUM('Low','Medium','High','Critical') NOT NULL,
    score_breakdown      JSON COMMENT 'Per-factor contribution, weights, explanation',
    FOREIGN KEY (org_id) REFERENCES organization(org_id) ON DELETE CASCADE,
    FOREIGN KEY (signal_id) REFERENCES security_signal(signal_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Financial Exposure (simulated / estimated)
-- ---------------------------------------------------------------------
CREATE TABLE financial_exposure (
    exposure_id                        INT AUTO_INCREMENT PRIMARY KEY,
    org_id                              INT NOT NULL,
    assessment_id                       INT NOT NULL,
    ransomware_exposure                 DECIMAL(18,2) DEFAULT 0,
    data_breach_exposure                DECIMAL(18,2) DEFAULT 0,
    business_interruption_exposure      DECIMAL(18,2) DEFAULT 0,
    incident_response_exposure          DECIMAL(18,2) DEFAULT 0,
    regulatory_legal_exposure           DECIMAL(18,2) DEFAULT 0,
    calculation_basis                   VARCHAR(50) DEFAULT 'SIMULATED',
    created_at                          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES organization(org_id) ON DELETE CASCADE,
    FOREIGN KEY (assessment_id) REFERENCES risk_assessment(assessment_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Policy (simulated insurance policy record)
-- ---------------------------------------------------------------------
CREATE TABLE policy (
    policy_id       INT AUTO_INCREMENT PRIMARY KEY,
    org_id          INT NOT NULL,
    policy_number   VARCHAR(50) UNIQUE NOT NULL,
    effective_date  DATE,
    expiry_date     DATE,
    status          ENUM('Active','Expired','Under Review') DEFAULT 'Active',
    FOREIGN KEY (org_id) REFERENCES organization(org_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Coverage (per-category limits within a policy)
-- ---------------------------------------------------------------------
CREATE TABLE coverage (
    coverage_id     INT AUTO_INCREMENT PRIMARY KEY,
    policy_id       INT NOT NULL,
    coverage_type   ENUM('Ransomware','Data Breach','Business Interruption',
                          'Incident Response','Third-Party Liability') NOT NULL,
    coverage_limit  DECIMAL(18,2) NOT NULL,
    deductible      DECIMAL(18,2) DEFAULT 0,
    FOREIGN KEY (policy_id) REFERENCES policy(policy_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Risk Alert
-- ---------------------------------------------------------------------
CREATE TABLE risk_alert (
    alert_id         INT AUTO_INCREMENT PRIMARY KEY,
    org_id           INT NOT NULL,
    assessment_id    INT NOT NULL,
    exposure_id      INT,
    previous_score   DECIMAL(5,2),
    current_score    DECIMAL(5,2),
    main_reason      TEXT,
    coverage_gap_summary TEXT,
    recommendation   TEXT,
    status           ENUM('Pending Analyst Review','Approved','Rejected',
                           'Info Requested') DEFAULT 'Pending Analyst Review',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES organization(org_id) ON DELETE CASCADE,
    FOREIGN KEY (assessment_id) REFERENCES risk_assessment(assessment_id) ON DELETE CASCADE,
    FOREIGN KEY (exposure_id) REFERENCES financial_exposure(exposure_id) ON DELETE SET NULL
);

-- ---------------------------------------------------------------------
-- Analyst Review (human-in-the-loop decision)
-- ---------------------------------------------------------------------
CREATE TABLE analyst_review (
    review_id      INT AUTO_INCREMENT PRIMARY KEY,
    alert_id       INT NOT NULL,
    analyst_name   VARCHAR(100) NOT NULL,
    decision       ENUM('Approve','Reject','Request Info') NOT NULL,
    comments       TEXT,
    reviewed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES risk_alert(alert_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Review History (full audit trail)
-- ---------------------------------------------------------------------
CREATE TABLE review_history (
    history_id   INT AUTO_INCREMENT PRIMARY KEY,
    alert_id     INT NOT NULL,
    action       VARCHAR(100) NOT NULL,
    notes        TEXT,
    action_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES risk_alert(alert_id) ON DELETE CASCADE
);

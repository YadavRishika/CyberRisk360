# CyberRisk360

### Guidewire-Oriented Cyber Risk Analytics & Insurance Review Accelerator

CyberRisk360 is a decision-support platform designed to assess changing cyber risk and connect cybersecurity signals with insurance coverage analysis.

The project uses real-world cyber incident data from the **EuRepoC Global Dataset** as a source for cybersecurity signals. These signals are processed and transformed into inputs for an explainable cyber-risk scoring model.

The insurance policy, coverage, and financial exposure components are modeled/simulated for demonstration purposes.

**CyberRisk360 does not calculate real insurance premiums, bind or issue policies, or make final underwriting decisions. All recommendations are intended for analyst review.**

---

## 1. Problem Statement

Cyber insurance decisions are often based on relatively static assessments of an organization's security posture, while cyber risks and vulnerabilities continuously evolve.

CyberRisk360 aims to provide an adaptive decision-support platform that:

- Tracks changing cybersecurity signals
- Calculates an explainable cyber-risk score
- Estimates modeled financial exposure
- Identifies potential insurance coverage gaps
- Generates risk alerts when risk changes significantly
- Provides an analyst review workflow
- Supports transparent, human-in-the-loop insurance analysis

---

## 2. Data Sources

### Real-world cybersecurity data

CyberRisk360 uses the **EuRepoC Global Dataset of Cyber Incidents** as a real-world source of cybersecurity incident information.

The dataset contains historical cyber incidents and attributes such as:

- Incident date
- Incident type
- Target/receiver information
- Country
- Threat actor information
- Impact characteristics
- Operational characteristics

The real incident data is transformed into security signals that can be processed by the CyberRisk360 risk engine.

### Modeled / simulated data

The following components are currently modeled or simulated for demonstration:

- Insurance policies
- Coverage limits
- Financial exposure estimates
- Coverage-gap calculations
- Analyst review decisions

This separation allows the project to use real cybersecurity information without claiming access to confidential insurance or financial data.

---

## 3. Project Architecture

The current data flow is:

```text
EuRepoC Real-World Cyber Incidents
                |
                v
      Data Transformation
                |
                v
        Security Signals
                |
                v
          Risk Engine
                |
                v
        Cyber Risk Score
                |
        +-------+-------+
        |               |
        v               v
  Risk Trend      Exposure Engine
                        |
                        v
              Modeled Financial Exposure
                        |
                        v
                  Gap Engine
                        |
                        v
              Coverage Gap Analysis
                        |
                        v
                  Alert Engine
                        |
                        v
                Analyst Dashboard
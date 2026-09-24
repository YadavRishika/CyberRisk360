import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Central configuration.
    Reads DB connection from environment variables so the project can be
    pointed at any local MySQL instance without touching code.

    Set these before running (examples for macOS/Linux shown; use `set` on
    Windows cmd or $env: on PowerShell):

        export DB_HOST=localhost
        export DB_PORT=3306
        export DB_USER=root
        export DB_PASSWORD=yourpassword
        export DB_NAME=cyberrisk360
    """
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "cyberrisk360")

    SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Risk alert trigger threshold: an alert is generated if the risk score
    # rises by at least this many points between two consecutive snapshots,
    # OR if any coverage gap > 0 is detected.
    RISK_INCREASE_ALERT_THRESHOLD = 8.0

    # Clearly and repeatedly disclosed across API responses and UI.
    DATA_DISCLAIMER = (
        "All security signals, risk scores, financial exposure figures, and "
        "coverage data in this system are SIMULATED for demonstration and "
        "decision-support purposes only. This platform does not calculate "
        "real insurance premiums, does not bind or issue policies, and does "
        "not represent guaranteed underwriting decisions. All outputs "
        "require human analyst review."
    )

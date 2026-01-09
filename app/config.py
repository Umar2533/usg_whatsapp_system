import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
NGROK_BASE_URL = os.getenv("NGROK_BASE_URL")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")

# Data paths
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "database"
WORD_REPORTS_DIR = DATA_DIR / "word_reports"
PDF_REPORTS_DIR = BASE_DIR / "static" / "pdf_reports"
LOG_DIR = BASE_DIR / "logs"

# Ensure folders exist
for path in [DB_DIR, WORD_REPORTS_DIR, PDF_REPORTS_DIR, LOG_DIR]:
    os.makedirs(path, exist_ok=True)

# Database
# DATABASE_URL = f"sqlite:///{DB_DIR}/usg.db"
# DB_PATH = DB_DIR / "usg.db"
# Database (FINAL)
DB_PATH = BASE_DIR / "data" / "database" / "reports.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"



import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env (local only, Railway ignores .env)
load_dotenv()

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================
# Environment Variables
# ======================
NGROK_BASE_URL = os.getenv("NGROK_BASE_URL")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")

# ======================
# Data Directories
# ======================
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "database"
WORD_REPORTS_DIR = DATA_DIR / "word_reports"

# ⚠️ PDFs static me hain (agar future me remove karna ho to easy hoga)
PDF_REPORTS_DIR = BASE_DIR / "static" / "pdf_reports"
LOG_DIR = BASE_DIR / "logs"

# Ensure folders exist (Railway-safe)
for path in [DB_DIR, WORD_REPORTS_DIR, PDF_REPORTS_DIR, LOG_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# ======================
# Database (SQLite)
# ======================
DB_PATH = DB_DIR / "reports.db"

# sqlite3 ke liye
DB_PATH_STR = str(DB_PATH)

# SQLAlchemy future-proof (agar later use karein)
DATABASE_URL = f"sqlite:///{DB_PATH_STR}"

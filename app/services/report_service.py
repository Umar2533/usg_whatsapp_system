from email import message
import os
import logging
from datetime import datetime
from urllib.parse import quote
from app.config import TWILIO_WHATSAPP_FROM
from app.services.reportlab_pdf import generate_pdf_from_word
from app.services.whatsapp_send import send_pdf_via_whatsapp
import sqlite3

# Directories
WORD_REPORTS_DIR = "data/word_reports"
PDF_REPORTS_DIR = "static/pdf_reports"
NGROK_BASE_URL = "https://goatishly-presageful-emmitt.ngrok-free.dev"
DB_PATH = "data/database/reports.db"

logger = logging.getLogger(__name__)

def process_report(word_file_path: str, whatsapp_number: str, patient_name: str):
    """
    1. Convert Word → PDF
    2. Save report info to DB (status = pending)
    3. WhatsApp sending is handled later by clinic_bot
    """

    if not os.path.exists(word_file_path):
        raise FileNotFoundError("Word file not found")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = patient_name.replace(" ", "_")
    pdf_file_name = f"USG_Report_{safe_name}_{timestamp}.pdf"
    pdf_path = os.path.join(PDF_REPORTS_DIR, pdf_file_name)

    os.makedirs(PDF_REPORTS_DIR, exist_ok=True)

    # --- Step 1: Word → PDF ---
    try:
        generate_pdf_from_word(word_file_path, pdf_path)
    except Exception as e:
        logger.error(f"PDF generation failed for {patient_name}: {e}")
        raise RuntimeError("PDF generation failed")

    # --- Step 2: Remove Word file (safe) ---
    try:
        if os.path.exists(word_file_path):
            os.remove(word_file_path)
    except Exception as e:
        logger.warning(f"Could not delete temp Word file: {e}")

    # --- Step 3: Save DB record ---
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO reports (patient_name, whatsapp_number, file_name, created_at, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (
            patient_name,
            whatsapp_number,
            pdf_path,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.critical(f"DB insert failed for {patient_name}: {e}")
        raise RuntimeError("Database insert failed")

    return pdf_path

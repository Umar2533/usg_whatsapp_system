# app/services/whatsapp_send.py

from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, NGROK_BASE_URL
from twilio.rest import Client
from urllib.parse import quote
import os
from app.database.db import update_report_status

def send_pdf_via_whatsapp(to_number: str, pdf_path: str, report_id: int, message: str = ""):
    """
    Send a PDF file via WhatsApp using Twilio and update DB status.
    """
    if not os.path.exists(pdf_path):
        print(f"[ERROR] PDF not found: {pdf_path}")
        update_report_status(report_id, "failed")
        return None

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    try:
        file_name = os.path.basename(pdf_path)
        media_url = f"{NGROK_BASE_URL}/static/pdf_reports/{quote(file_name)}"

        msg = client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=to_number,
            body=message,
            media_url=[media_url]
        )

        print(f"[INFO] PDF sent to {to_number}, SID: {msg.sid}")
        update_report_status(report_id, "sent")
        return msg.sid

    except Exception as e:
        print(f"[ERROR] Failed to send PDF: {e}")
        update_report_status(report_id, "failed")
        return None

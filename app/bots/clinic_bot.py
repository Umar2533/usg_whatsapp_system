# bot/clinic_bot.py

from app.services.whatsapp_send import send_pdf_via_whatsapp
import sqlite3

DB_PATH = "data/database/reports.db"

# Temporary memory per session to handle state
USER_STATE = {}


def get_report_by_id(report_id: int):
    """
    Fetch PDF file path from DB for given report ID.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT pdf_file FROM reports WHERE id = ?", (report_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def get_bot_response(user_msg: str, user_phone: str):
    """
    Main bot logic:
    1. User sends 'report <id>'
    2. Bot asks for patient name
    3. User sends patient name
    4. Bot sends PDF via WhatsApp with patient name in message
    """
    msg = user_msg.strip()

    # STEP 2: If waiting for patient name
    if USER_STATE.get(user_phone, {}).get("waiting_for_name"):
        report_id = USER_STATE[user_phone]["report_id"]
        patient_name = msg

        pdf_path = get_report_by_id(report_id)
        if not pdf_path:
            USER_STATE.pop(user_phone, None)
            return "❌ Report not found."

        # ✅ Custom message for WhatsApp
        custom_message = f"Your report ({patient_name}) is ready. Thanks for visit 📄"

        # Send PDF and update status in DB
        sid = send_pdf_via_whatsapp(
            to_number=user_phone,
            pdf_path=pdf_path,
            report_id=report_id,
            message=custom_message
        )

        USER_STATE.pop(user_phone, None)
        if sid:
            return f"📄 Report #{report_id} sent successfully."
        else:
            return f"❌ Failed to send Report #{report_id}. Check logs."

    # STEP 1: User sends 'report <id>'
    if msg.lower().startswith("report"):
        parts = msg.split()
        if len(parts) != 2 or not parts[1].isdigit():
            return "❌ Use format: report <id>"

        report_id = int(parts[1])

        # Check if report exists in DB
        pdf_path = get_report_by_id(report_id)
        if not pdf_path:
            return f"❌ Report #{report_id} does not exist."

        # Mark user state to wait for patient name
        USER_STATE[user_phone] = {
            "waiting_for_name": True,
            "report_id": report_id
        }

        return "Please send patient name 👤"

    # Default message for any other input (strict)
    return "Hello 👋\nSend: report <id>"

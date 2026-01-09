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

# # bot/clinic_bot.py

# from app.services.whatsapp_send import send_pdf_via_whatsapp
# from app.database.db import get_report_by_id, update_report_status
# import sqlite3

# DB_PATH = "data/database/reports.db"

# # Temporary memory per session to track waiting for patient name
# USER_STATE = {}

# # Only "report <id>" flow allowed for users
# ALLOWED_USER_COMMANDS = ["report"]


# def get_bot_response(user_msg: str, user_phone: str):
#     msg = user_msg.strip()

#     # STEP 2: Waiting for patient name
#     if USER_STATE.get(user_phone, {}).get("waiting_for_name"):
#         report_id = USER_STATE[user_phone]["report_id"]
#         patient_name = msg

#         pdf_path = get_report_by_id(report_id)
#         if not pdf_path:
#             USER_STATE.pop(user_phone, None)
#             return "❌ Report not found."

#         # Send PDF and update status in DB
#         sid = send_pdf_via_whatsapp(
#             to_number=user_phone,
#             pdf_path=pdf_path,
#             report_id=report_id,
#             message=f"Here is your report, {patient_name} ✅"
#         )

#         # Remove user from waiting state
#         USER_STATE.pop(user_phone, None)

#         if sid:
#             return f"📄 Report #{report_id} sent successfully."
#         else:
#             return f"❌ Failed to send Report #{report_id}. Check logs."

#     # STEP 1: report <id>
#     parts = msg.split()
#     if parts[0].lower() in ALLOWED_USER_COMMANDS:
#         if len(parts) != 2 or not parts[1].isdigit():
#             return "❌ Use format: report <id>"

#         report_id = int(parts[1])
#         pdf_path = get_report_by_id(report_id)
#         if not pdf_path:
#             return f"❌ Report #{report_id} does not exist."

#         # Store waiting state to get patient name next
#         USER_STATE[user_phone] = {
#             "waiting_for_name": True,
#             "report_id": report_id
#         }
#         return "Please send patient name 👤"

#     # Default fallback for any other user message
#     return "Hello 👋\nSend: report <id>"

# # bot/clinic_bot.py

# from app.services.whatsapp_send import send_pdf_via_whatsapp
# import sqlite3
# from app.database.db import update_report_status

# DB_PATH = "data/database/reports.db"

# # Temporary memory per session
# USER_STATE = {}


# def get_report_by_id(report_id: int):
#     """Fetch PDF path from DB by report ID"""
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT pdf_file FROM reports WHERE id = ?", (report_id,))
#     row = c.fetchone()
#     conn.close()
#     return row[0] if row else None


# def get_bot_response(user_msg: str, user_phone: str):
#     """Strict bot response flow: report <id> -> patient name -> PDF send"""
#     msg = user_msg.strip()

#     # STEP 2: Waiting for patient name
#     if USER_STATE.get(user_phone, {}).get("waiting_for_name"):
#         report_id = USER_STATE[user_phone]["report_id"]
#         patient_name = msg

#         pdf_path = get_report_by_id(report_id)
#         if not pdf_path:
#             USER_STATE.pop(user_phone, None)
#             return "❌ Report not found."

#         # Send PDF and update status
#         sid = send_pdf_via_whatsapp(
#             to_number=user_phone,
#             pdf_path=pdf_path,
#             report_id=report_id,
#             message=f"Here is your report, {patient_name} ✅"
#         )

#         USER_STATE.pop(user_phone, None)
#         if sid:
#             return f"📄 Report #{report_id} sent successfully."
#         else:
#             return f"❌ Failed to send Report #{report_id}. Check logs."

#     # STEP 1: Start with "report <id>"
#     if msg.lower().startswith("report"):
#         parts = msg.split()
#         if len(parts) != 2 or not parts[1].isdigit():
#             return "❌ Invalid format. Use: report <id>"

#         report_id = int(parts[1])

#         # Check if report exists in DB
#         pdf_path = get_report_by_id(report_id)
#         if not pdf_path:
#             return f"❌ Report #{report_id} does not exist."

#         # Set session for patient name input
#         USER_STATE[user_phone] = {
#             "waiting_for_name": True,
#             "report_id": report_id
#         }

#         return "Please send patient name 👤"

#     # STRICT: All other messages ignored politely
#     return "⚠️ Only valid commands are allowed.\nSend: report <id>"

# # bot/clinic_bot.py

# from app.services.whatsapp_send import send_pdf_via_whatsapp
# from app.database.db import update_report_status, delete_report
# import sqlite3

# DB_PATH = "data/database/reports.db"
# USER_STATE = {}  # Temporary memory per session


# def get_report_by_id(report_id: int):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT pdf_file FROM reports WHERE id = ?", (report_id,))
#     row = c.fetchone()
#     conn.close()
#     return row[0] if row else None


# def get_bot_response(user_msg: str, user_phone: str):
#     msg = user_msg.strip()

#     # STEP 2: Waiting for patient name
#     if USER_STATE.get(user_phone, {}).get("waiting_for_name"):
#         report_id = USER_STATE[user_phone]["report_id"]
#         patient_name = msg

#         pdf_path = get_report_by_id(report_id)
#         if not pdf_path:
#             USER_STATE.pop(user_phone, None)
#             return "❌ Report not found."

#         # Send PDF and update DB status
#         sid = send_pdf_via_whatsapp(
#             to_number=user_phone,
#             pdf_path=pdf_path,
#             report_id=report_id,
#             message=f"Here is your report, {patient_name} ✅"
#         )

#         USER_STATE.pop(user_phone, None)
#         if sid:
#             return f"📄 Report #{report_id} sent successfully."
#         else:
#             return f"❌ Failed to send Report #{report_id}. Check logs."

#     # STEP 1: report <id>
#     if msg.lower().startswith("report"):
#         parts = msg.split()
#         if len(parts) != 2 or not parts[1].isdigit():
#             return "❌ Use format: report <id>"

#         report_id = int(parts[1])

#         # Check if report exists in DB
#         pdf_path = get_report_by_id(report_id)
#         if not pdf_path:
#             return f"❌ Report #{report_id} does not exist."

#         USER_STATE[user_phone] = {
#             "waiting_for_name": True,
#             "report_id": report_id
#         }

#         return "Please send patient name 👤"

#     # Optional: handle delete command
#     if msg.lower().startswith("delete"):
#         parts = msg.split()
#         if len(parts) == 2 and parts[1].isdigit():
#             report_id = int(parts[1])
#             delete_report(report_id)
#             return f"🗑 Report #{report_id} deleted from DB."
#         else:
#             return "❌ Use format: delete <id>"

#     return "Hello 👋\nSend: report <id>"


# # bot/clinic_bot.py

# from app.services.whatsapp_send import send_pdf_via_whatsapp
# import sqlite3
# from app.database.db import update_report_status

# DB_PATH = "data/database/reports.db"

# # Temporary memory (per session)
# USER_STATE = {}


# def get_report_by_id(report_id: int):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute(
#         "SELECT pdf_file FROM reports WHERE id = ?",
#         (report_id,)
#     )
#     row = c.fetchone()
#     conn.close()
#     return row[0] if row else None


# def get_bot_response(user_msg: str, user_phone: str):
#     msg = user_msg.strip()

#     # STEP 2: If waiting for patient name
#     if USER_STATE.get(user_phone, {}).get("waiting_for_name"):
#         report_id = USER_STATE[user_phone]["report_id"]
#         patient_name = msg

#         pdf_path = get_report_by_id(report_id)
#         if not pdf_path:
#             USER_STATE.pop(user_phone, None)
#             return "❌ Report not found."

#         # Send PDF and update status in DB
#         sid = send_pdf_via_whatsapp(
#             to_number=user_phone,
#             pdf_path=pdf_path,
#             report_id=report_id,
#             message=f"Here is your report, {patient_name} ✅"
#         )

#         USER_STATE.pop(user_phone, None)
#         if sid:
#             return f"📄 Report #{report_id} sent successfully."
#         else:
#             return f"❌ Failed to send Report #{report_id}. Check logs."

#     # STEP 1: report <id>
#     if msg.lower().startswith("report"):
#         parts = msg.split()
#         if len(parts) != 2 or not parts[1].isdigit():
#             return "❌ Use format: report <id>"

#         report_id = int(parts[1])

#         # Check if report exists in DB
#         pdf_path = get_report_by_id(report_id)
#         if not pdf_path:
#             return f"❌ Report #{report_id} does not exist."

#         USER_STATE[user_phone] = {
#             "waiting_for_name": True,
#             "report_id": report_id
#         }

#         return "Please send patient name 👤"

#     return "Hello 👋\nSend: report <id>"

# # bot/clinic_bot.py

# from app.services.whatsapp_send import send_pdf_via_whatsapp
# import sqlite3

# DB_PATH = "data/database/reports.db"
# # Temporary memory (per session)
# USER_STATE = {}


# def get_report_by_id(report_id: int):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute(
#         "SELECT pdf_file FROM reports WHERE id = ?",
#         (report_id,)
#     )
#     row = c.fetchone()
#     conn.close()
#     return row[0] if row else None


# from app.services.whatsapp_send import send_pdf_via_whatsapp
# import sqlite3

# DB_PATH = "data/database/reports.db"
# USER_STATE = {}


# def get_report_by_id(report_id: int):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT pdf_file FROM reports WHERE id = ?", (report_id,))
#     row = c.fetchone()
#     conn.close()
#     return row[0] if row else None


# def get_bot_response(user_msg: str, user_phone: str):
#     msg = user_msg.strip()

#     # STEP 2: If waiting for patient name
#     if USER_STATE.get(user_phone, {}).get("waiting_for_name"):
#         report_id = USER_STATE[user_phone]["report_id"]
#         patient_name = msg

#         pdf_path = get_report_by_id(report_id)
#         if not pdf_path:
#             USER_STATE.pop(user_phone, None)
#             return "❌ Report not found."

#         send_pdf_via_whatsapp(
#             to_number=user_phone,
#             pdf_path=pdf_path,
#             message=f"Here is your report, {patient_name} ✅"
#         )

#         USER_STATE.pop(user_phone, None)
#         return f"📄 Report #{report_id} sent successfully."


#     # STEP 1: report <id>
#     if msg.lower().startswith("report"):
#         parts = msg.split()

#         if len(parts) != 2 or not parts[1].isdigit():
#             return "❌ Use format: report <id>"

#         USER_STATE[user_phone] = {
#             "waiting_for_name": True,
#             "report_id": int(parts[1])
#         }

#         return "Please send patient name 👤"

#     return "Hello 👋\nSend: report <id>"



# # app/bots/clinic_bot.py
# def get_bot_response(user_msg: str):
#     """
#     Simple rule-based bot for clinic reports
#     """
#     msg = user_msg.lower().strip()

#     if "hi" in msg or "hello" in msg:
#         return "Hello 👋 Welcome to the USG Clinic Bot!"
#     elif "status" in msg:
#         return "Please provide report ID to check status: e.g., 'report 123'"
#     elif "report" in msg:
#         # Extract report number (very simple logic)
#         parts = msg.split()
#         if len(parts) == 2 and parts[1].isdigit():
#             report_id = parts[1]
#             return f"Report {report_id} is ready. PDF will be sent shortly."
#         else:
#             return "Invalid report command. Use: 'report <id>'"
#     else:
#         return "I am not sure about that. You can say 'hi' or 'status'."


# from app.services.whatsapp_send import send_pdf_via_whatsapp
# from app.database.models import Report

# def get_bot_response(user_msg: str, user_phone: str):
#     msg = user_msg.lower().strip()

#     if "report" in msg:
#         parts = msg.split()
#         if len(parts) == 2 and parts[1].isdigit():
#             report_id = int(parts[1])

#             # Fetch PDF path from DB (example using SQLAlchemy)
#             report = Report.get_by_id(report_id)  # implement this method
#             if report and report.pdf_file:
#                 send_pdf_via_whatsapp(
#                     to_number=user_phone,
#                     pdf_path=report.pdf_file,
#                     message=f"Here is your report #{report_id}"
#                 )
#                 return f"Report {report_id} sent to your WhatsApp ✅"
#             else:
#                 return "Report not found or PDF not ready."
#         else:
#             return "Invalid report command. Use: 'report <id>'"
#     return "I am not sure about that. You can say 'report <id>'."

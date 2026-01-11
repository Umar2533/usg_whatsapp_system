from fastapi import (
    FastAPI, Request, Form, UploadFile, File,
    BackgroundTasks, Query
)
from app.database.db import get_connection, init_db
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import sqlite3
import os
import shutil
import re
import tempfile
import shutil
from pathlib import Path
from fastapi.responses import JSONResponse
from datetime import datetime
from app.services.whatsapp_send import send_pdf_via_whatsapp
from app.services.word_to_pdf import word_to_pdf
from app.config import DB_PATH, PDF_REPORTS_DIR

#from init_db import init_db
from app.database.db import init_db

from app.services.report_service import NGROK_BASE_URL, process_report
from urllib.parse import quote
import os


# ================== APP INIT ==================
app = FastAPI(title="USG Clinic Bot System")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

WORD_DIR = "data/word_reports"


os.makedirs(WORD_DIR, exist_ok=True)


# ================== STARTUP ==================
@app.on_event("startup")
def startup():
    init_db()


# ================== UI ==================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ================== GET REPORTS ==================
@app.get("/get_reports")
def get_reports(
    selected_date: str | None = Query(default=None)
):
    conn = get_connection()
    cursor = conn.cursor()

    if selected_date:
        cursor.execute("""
            SELECT id, patient_name, file_name, whatsapp_number, created_at, status
            FROM reports
            WHERE date(created_at)=?
            ORDER BY created_at DESC
        """, (selected_date,))
    else:
        cursor.execute("""
            SELECT id,patient_name, file_name, whatsapp_number, created_at, status
            FROM reports
            ORDER BY created_at DESC
        """)

    rows = cursor.fetchall()
    conn.close()

    reports = [
        {   
            "id": r[0],     
            "patient_name": r[1],
            "file_name": r[2],
            "whatsapp_number": r[3],
            "created_at": r[4],
            "status": r[5]
        }
        for r in rows
    ]

    return {"status": "success", "reports": reports}



# ================== SUMMARY ==================
@app.get("/summary_counts")
def summary_counts():
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    week = datetime.now().strftime("%W")
    month = datetime.now().strftime("%m")

    cursor.execute("SELECT COUNT(*) FROM reports WHERE date(created_at)=?", (today,))
    today_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE strftime('%W', created_at)=?", (week,))
    week_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE strftime('%m', created_at)=?", (month,))
    month_count = cursor.fetchone()[0]

    conn.close()

    return {
        "today": today_count,
        "week": week_count,
        "month": month_count
    }
# show date in format 06 Jan 2026 in the reports send via whatsapp

def format_report_date(created_at: str):
    dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%A, %d %b %Y")
@app.post("/add_report")
async def add_report(
    background_tasks: BackgroundTasks,
    patient_name: str = Form(...),
    whatsapp_number: str = Form(...),
    word_file: UploadFile = File(...)
):
    # ---------- Validations ----------
    if not re.match(r"^\+92\d{10}$", whatsapp_number):
        return JSONResponse(
            {"status": "error", "message": "Invalid WhatsApp number"},
            status_code=400
        )

    if not word_file.filename.lower().endswith(".docx"):
        return JSONResponse(
            {"status": "error", "message": "Only .docx files are allowed"},
            status_code=400
        )

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------- Save Word temporarily ----------
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_word:
        shutil.copyfileobj(word_file.file, tmp_word)
        tmp_word_path = tmp_word.name

    try:
        # ---------- Generate PDF ----------
        PDF_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        pdf_path = word_to_pdf(tmp_word_path, safe_name=True)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"PDF generation failed: {str(e)}"}
        )
    finally:
        # Cleanup temporary Word file
        if os.path.exists(tmp_word_path):
            os.remove(tmp_word_path)

    pdf_filename = os.path.basename(pdf_path)
    safe_filename = quote(pdf_filename)

    # ---------- Database Insert ----------
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reports (patient_name, file_name, whatsapp_number, created_at, status)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_name, safe_filename, whatsapp_number, created_at, "pending"))
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # ---------- Background WhatsApp Task ----------
    clean_name = patient_name.strip().upper()
    report_date = format_report_date(created_at)
    background_tasks.add_task(
        send_pdf_via_whatsapp,
        f"whatsapp:{whatsapp_number}",
        pdf_path,
        report_id,
        f"*{clean_name}*\nYour medical report dated *{report_date}* is ready.\nThank you for visiting us. 📄"
    )

    # ---------- Return JSON ----------
    return {
        "status": "success",
        "message": f"Report for {patient_name} added successfully",
        "report": {
            "id": report_id,
            "patient_name": patient_name,
            "file_name": safe_filename,
            "whatsapp_number": whatsapp_number,
            "created_at": created_at,
            "status": "pending"
        }
    }
# @app.post("/add_report")
# async def add_report(
#     background_tasks: BackgroundTasks,
#     patient_name: str = Form(...),
#     whatsapp_number: str = Form(...),
#     word_file: UploadFile = File(...)
# ):
#     # ---------- validations ----------
#     if not re.match(r"^\+92\d{10}$", whatsapp_number):
#         return JSONResponse({"status": "error", "message": "Invalid WhatsApp number"}, status_code=400)

#     if not word_file.filename.lower().endswith(".docx"):
#         return JSONResponse({"status": "error", "message": "Only .docx allowed"}, status_code=400)

#     created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     # Save Word temporarily
#     with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_word:
#         shutil.copyfileobj(word_file.file, tmp_word)
#         tmp_word_path = tmp_word.name
    
#     # Generate PDF in static folder
#     PDF_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
#     pdf_path = word_to_pdf(tmp_word_path, safe_name=True)
#     pdf_filename = os.path.basename(pdf_path)
#     safe_filename = quote(pdf_filename)

#     # ---------- DB Insert with status ----------
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO reports (patient_name, file_name, whatsapp_number, created_at, status)
#         VALUES (?, ?, ?, ?, ?)
#     """, (patient_name, safe_filename, whatsapp_number, created_at, "pending"))
#     report_id = cursor.lastrowid  # <-- for WhatsApp
#     conn.commit()
#     conn.close()

#     # ---------- Background WhatsApp task ----------
#     clean_name = patient_name.strip().upper()
#     report_date = format_report_date(created_at)
#     background_tasks.add_task(
#         send_pdf_via_whatsapp,
#         f"whatsapp:{whatsapp_number}",
#         pdf_path,
#         report_id,
#         #f" {patient_name} : Your Report  is ready. Thanks for visit 📄"
#         f"*{clean_name}*\n"
#         f"Your medical report dated *{report_date}* is ready.\n"
#         "Thank you for visiting us. 📄"
#     )

#     return {
#         "status": "success",
#         "message": f"Report for {patient_name} added successfully",
#         "report": {
#             "id": report_id,
#             "patient_name": patient_name,
#             "file_name": safe_filename,
#             "whatsapp_number": whatsapp_number,
#             "created_at": created_at,
#             "status": "pending"
#         }
#     }


from fastapi.responses import PlainTextResponse

REPLIED_NUMBERS = set()

@app.post("/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    if From in REPLIED_NUMBERS:
        return PlainTextResponse("")  # 🔕 silent

    REPLIED_NUMBERS.add(From)

    return PlainTextResponse(
        "Thank you for contacting us.\n"
        "Your medical report will be sent automatically once ready. 📄"
    )

# ================== RESEND REPORT ==================
@app.post("/resend_report/{report_id}")
def resend_report(report_id: int, background_tasks: BackgroundTasks):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT file_name, whatsapp_number, patient_name, created_at
        FROM reports
        WHERE id = ?
    """, (report_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return {"status": "error", "message": "Report not found"}

    file_name, whatsapp, patient_name, created_at = row
    pdf_path = f"static/pdf_reports/{file_name}"

    
    # ---------- Background WhatsApp task ----------
    clean_name = patient_name.strip().upper()
    report_date = format_report_date(created_at)
    background_tasks.add_task(
        send_pdf_via_whatsapp,
        f"whatsapp:{whatsapp}",
        pdf_path,
        report_id,
        #f" {patient_name} : Your Report  is ready. Thanks for visit 📄"
        f"*{clean_name}*\n"
        f"Your medical report dated *{report_date}* is ready and sent you again.\n"
        "Thank you for visiting us. 📄"
    )


    return {"status": "success", "message": "Report resend initiated"}

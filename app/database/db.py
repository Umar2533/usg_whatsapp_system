

import sqlite3
from app.config import DB_PATH_STR

def get_connection():
    return sqlite3.connect(DB_PATH_STR)



def init_db():
    """
    Initialize SQLite database and create table if not exists
    """
   
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            whatsapp_number TEXT NOT NULL,
            file_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()


def save_report_to_db(
    patient_name: str,
    whatsapp_number: str,
    file_name: str,
    created_at: str,
    status: str = "pending"
):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO reports (patient_name, whatsapp_number, file_name, created_at, status)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_name, whatsapp_number, file_name, created_at, status))
    conn.commit()
    conn.close()



def fetch_reports():
    """
    Fetch all reports ordered by latest first
    Returns tuples:
    (id, patient_name, file_name, whatsapp_number, created_at, status)
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT
            id,
            patient_name,
            file_name,
            whatsapp_number,
            created_at,
            status
        FROM reports
        ORDER BY created_at DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows



def get_report_by_id(report_id: int):
    """
    Get PDF file path for a given report ID
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT file_name FROM reports WHERE id = ?", (report_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def update_report_status(report_id: int, status: str):
    """
    Update the status of a report
    status: 'pending', 'sent', 'failed'
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE reports
        SET status = ?
        WHERE id = ?
    """, (status, report_id))
    conn.commit()
    conn.close()


def update_report(report_id: int, patient_name: str = None, file_name: str = None):
    """
    Update report details (patient name or file name)
    """
    conn = get_connection()
    c = conn.cursor()
    if patient_name and file_name:
        c.execute("""
            UPDATE reports
            SET patient_name = ?, file_name = ?
            WHERE id = ?
        """, (patient_name, file_name, report_id))
    elif patient_name:
        c.execute("""
            UPDATE reports
            SET patient_name = ?
            WHERE id = ?
        """, (patient_name, report_id))
    elif file_name:
        c.execute("""
            UPDATE reports
            SET file_name = ?
            WHERE id = ?
        """, (file_name, report_id))
    conn.commit()
    conn.close()


def delete_report(report_id: int):
    """
    Delete a report from the database
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        DELETE FROM reports
        WHERE id = ?
    """, (report_id,))
    conn.commit()
    conn.close()

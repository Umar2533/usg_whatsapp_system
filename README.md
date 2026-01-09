# USG WhatsApp Report Delivery System

A production-grade system for clinics to automatically convert medical reports from Word to PDF, store them securely, and deliver them to patients via WhatsApp. The system is designed with clear separation of concerns, audit logging, and extensibility in mind.

---

## Overview

This project enables clinic staff to upload patient reports, automatically generate PDFs, store metadata in a database, and send reports to patients through WhatsApp. Patients can request their reports using a simple WhatsApp command, while unsolicited messages are safely ignored or handled with a polite response.

---

## High-Level Architecture

### Admin / Clinic Flow

1. Admin uploads a Word report file
2. PDF is generated automatically
3. Report metadata is stored in the database
4. WhatsApp message with PDF link is sent to the patient
5. Delivery status is tracked (`sent` / `failed`)
6. Admin can resend the report at any time

### Patient Flow

- Any random message → ignored or replied with a single polite response
- Valid report request → report is delivered if available

---

## Proposed System Flow

### Clinic System (Typist / Admin UI)

- The clinic staff uses a browser-based or desktop interface
- Selects:
  - A Word report file (`.docx`)
  - Patient WhatsApp number
  - Optional patient identifier (e.g. name or internal ID)

### Word to PDF Conversion

- Upon submission:
  - Backend service converts the Word document to a PDF
  - Generated PDF is saved in a public static directory

### Database Logging

- The system stores:
  - Word file path
  - PDF file path
  - Patient identifier
  - WhatsApp number
  - Timestamp
- This provides full traceability and audit history

### WhatsApp Delivery

- The backend sends the PDF (or public link) to the patient’s WhatsApp number
- Delivery status is recorded

### UI Feedback

- The UI displays:
  - Success message when delivery succeeds
  - Error message if delivery fails

---

## Advantages

- Each patient report is handled independently
- Fully automated PDF generation and WhatsApp delivery
- UI can be used for testing without affecting backend logic
- Database logging enables auditing, troubleshooting, and resending
- Modular design allows easy future enhancements

---

## Project Structure

usg_whatsapp_system/
│
├── app/
│   ├── main.py                 # Application entry point
│   ├── config.py               # Environment and configuration settings
│   │
│   ├── database/
│   │   ├── db.py               # Database connection
│   │   ├── init_db.py          # Database initialization
│   │   └── models.py           # Database models
│   │
│   ├── services/
│   │   ├── word_to_pdf.py      # Word → PDF conversion logic
│   │   ├── whatsapp_send.py    # WhatsApp sending service
│   │   ├── folder_watcher.py   # Automated folder monitoring
│   │   └── report_service.py   # Core report processing logic
│   │
│   ├── bots/
│   │   └── clinic_bot.py       # WhatsApp bot command handling
│   │
│   └── utils/
│       └── security.py         # Security and validation helpers
│
├── data/
│   ├── word_reports/           # Uploaded Word files
│   └── database/               # SQLite database files
│
├── static/
│   └── pdf_reports/            # Generated PDF reports
│
├── logs/                       # Application logs
│
├── tests/
│   └── test_services.py        # Unit tests
│
├── requirements.txt
└── README.md

---

## End-to-End Flow Summary


WhatsApp Input
↓
Bot Command Parsing
↓
Database Lookup (Patients / Reports)
↓
Word → PDF Conversion
↓
WhatsApp PDF Delivery
↓
(UI controls and monitoring only)

---

## Report Processing Flow (Detailed)


Typist Uploads Word File
│
▼
word_to_pdf()
│
▼
PDF Path Returned
│
▼
Save Metadata in Database
│
▼
Patient Requests Report via WhatsApp
│
▼
WhatsApp Bot Fetches PDF Path
│
▼
send_pdf_via_whatsapp()
│
▼
PDF Delivered to Patient

- The PDF generator returns the **full absolute or static path**, for example:

static/pdf_reports/sample_report.pdf
- This path is used for both database storage and WhatsApp delivery.

---

## Core Service Logic (Conceptual)

```python
def process_report(word_file_path: str, whatsapp_number: str, patient_name: str):
  # 1. Validate file existence
  # 2. Define PDF output path
  # 3. Generate PDF
  # 4. Store metadata in database
  # 5. Send PDF via WhatsApp


WhatsApp Bot Flow
/whatsapp
   |
   |--> Parse user command
   |--> "Your report is being prepared..."
   |
   |--> process_report(report_id)
           |--> word_to_pdf()
           |--> send_pdf_via_whatsapp()


Example Patient Interaction
Patient sends:
report 123

System behavior:


Locates the associated Word report


Checks if PDF already exists (or generates it)


Sends the PDF link via WhatsApp


WhatsApp reply:
Your report is ready 📄
Download here:
<public_pdf_link>


Database Schema (Simplified)
reports
(
  id,
  patient_name,
  pdf_file,
  whatsapp_number,
  created_at
)


Current Status


Application server running


Database initialized


WhatsApp bot operational


Architecture finalized and production-ready



Next Development Steps


Word → PDF conversion enhancement


Automated folder watcher


Lightweight web-based admin UI



License
This project is intended for educational and internal system use.
Adapt and extend according to your organization’s compliance and security requirements.

---

If you want, next I can:
- Optimize this README for **open-source** style  
- Add **architecture diagrams (Mermaid)**  
- Write **installation & deployment steps**  
- Or prepare a **GitHub release-ready version**

Just tell me 👍

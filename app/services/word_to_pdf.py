from pathlib import Path
from docx2pdf import convert
from app.config import PDF_REPORTS_DIR
from urllib.parse import quote
from datetime import datetime

def word_to_pdf(word_file_path: str, pdf_path: str = None, patient_name: str = "Patient", safe_name: bool = True):
    """
    Convert a Word document to PDF with:
    - Patient name
    - Timestamp
    - Unique filename (avoids overwriting)
    """

    word_path = Path(word_file_path)
    if not word_path.exists():
        raise FileNotFoundError(f"Word file not found: {word_file_path}")

    # Clean patient name
    patient_clean = patient_name.replace(" ", "_") if safe_name else patient_name

    # Base filename
    base_filename = f"USG_Report_{patient_clean}"

    # Timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}.pdf"

    # Set PDF path
    if pdf_path is None:
        pdf_path = PDF_REPORTS_DIR / filename
    else:
        pdf_path = Path(pdf_path)

    # Ensure folder exists
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # If file exists (extremely rare, same patient same second)
    counter = 1
    while pdf_path.exists():
        filename = f"{base_filename}_{timestamp}_{counter}.pdf"
        pdf_path = PDF_REPORTS_DIR / filename
        counter += 1

    # Convert Word to PDF
    convert(str(word_path), str(pdf_path))

    print(f"[INFO] Converted -> {pdf_path}")
    return str(pdf_path)

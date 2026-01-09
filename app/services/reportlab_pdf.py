# app/services/reportlab_pdf.py
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document


def generate_pdf_from_word(word_path: str, pdf_path: str):
    """
    Generate PDF using ReportLab from a Word (.docx) file.
    """
    try:
        if not os.path.exists(word_path):
            raise FileNotFoundError(f"Word file not found: {word_path}")

        doc = Document(word_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

        if not paragraphs:
            raise ValueError("Word file is empty")

        # Create PDF
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        y_pos = height - 50

        for line in paragraphs:
            c.drawString(40, y_pos, line)
            y_pos -= 15
            if y_pos < 40:
                c.showPage()
                y_pos = height - 50

        c.save()

    except Exception as e:
        raise RuntimeError(f"PDF generation failed: {e}")


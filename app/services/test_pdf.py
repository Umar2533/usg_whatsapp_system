from app.services.reportlab_pdf import generate_pdf_from_word

try:
    generate_pdf_from_word(
        "data/word_reports/CT.docx",
        "static/pdf_reports/CT.pdf"
    )
    print("PDF generated successfully!")
except Exception as e:
    print("PDF generation failed:", e)

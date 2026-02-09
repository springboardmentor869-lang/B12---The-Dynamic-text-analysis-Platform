import fitz  # PyMuPDF

def extract_text(pdf_path):
    """Extract text from a PDF using PyMuPDF"""
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

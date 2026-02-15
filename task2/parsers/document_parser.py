import pdfplumber
from docx import Document

def extract_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def extract_docx(path):
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])
    
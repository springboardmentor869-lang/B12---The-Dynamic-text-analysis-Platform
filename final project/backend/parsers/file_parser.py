import os
import fitz  # PyMuPDF
from docx import Document


def extract_text_from_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)

    for page in doc:
        text += page.get_text()

    doc.close()
    return text


def extract_text_from_docx(file_path):
    text = ""
    doc = Document(file_path)

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    elif ext == ".docx":
        return extract_text_from_docx(file_path)

    elif ext == ".txt":
        return extract_text_from_txt(file_path)

    else:
        raise ValueError("Unsupported file format. Only PDF, DOCX, and TXT are supported.")
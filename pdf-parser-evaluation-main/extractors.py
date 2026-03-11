import fitz  # PyMuPDF
import pdfplumber
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text

def extract_pymupdf(path):
    text = ""
    doc = fitz.open(path)
    for page in doc:
        text += page.get_text()
    return text

def extract_pdfplumber(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_pypdf2(path):
    text = ""
    reader = PdfReader(path)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_pdfminer(path):
    return extract_text(path)
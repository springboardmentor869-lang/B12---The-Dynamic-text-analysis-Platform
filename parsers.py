import os
import subprocess
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text as pdfminer_extract_text
from docx import Document
from PIL import Image
import pytesseract

def extract_text_pymupdf(path):
    doc = fitz.open(path)
    parts = []
    for page in doc:
        parts.append(page.get_text("text"))
    return "\n".join(parts).strip()

def extract_text_pdfminer(path):
    return pdfminer_extract_text(path).strip()

def extract_text_pdftotext(path, poppler_path=None):
    cmd = ["pdftotext", "-layout", path, "-"]
    env = None
    if poppler_path:
        env = os.environ.copy()
        env["PATH"] = poppler_path + os.pathsep + env.get("PATH", "")
    proc = subprocess.run(cmd, capture_output=True, env=env)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf8"))
    return proc.stdout.decode("utf8").strip()

def extract_text_docx(path):
    doc = Document(path)
    paras = [p.text for p in doc.paragraphs]
    return "\n".join(paras).strip()

def extract_text_ocr(path, dpi=200):
    doc = fitz.open(path)
    parts = []
    for page in doc:
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img)
        parts.append(text)
    return "\n".join(parts).strip()

PARSERS = {
    "pymupdf": extract_text_pymupdf,
    "pdfminer": extract_text_pdfminer,
    "pdftotext": extract_text_pdftotext,
    "ocr": extract_text_ocr,
    "docx": extract_text_docx,
}
"""
parsers.py - minimal in-process parsers.

Provides a PARSERS dict mapping parser names to functions that accept a path
and return a string (extracted text).

Requires (only if you use a parser):
- pymupdf: pip install pymupdf
- python-docx: pip install python-docx
- pytesseract + tesseract installed + Pillow: pip install pytesseract Pillow
"""
from typing import Callable, Dict

def extract_text_pymupdf(path: str) -> str:
    try:
        import fitz  # PyMuPDF
    except Exception as e:
        raise ImportError("PyMuPDF required: pip install pymupdf") from e
    doc = fitz.open(path)
    pages = []
    for p in doc:
        pages.append(p.get_text("text") or "")
    return "\n".join(pages).strip()

def extract_text_docx(path: str) -> str:
    try:
        from docx import Document
    except Exception as e:
        raise ImportError("python-docx required: pip install python-docx") from e
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs).strip()

def extract_text_ocr(path: str, dpi: int = 200) -> str:
    try:
        import fitz
        from PIL import Image
        import pytesseract
    except Exception as e:
        raise ImportError("For OCR install: pip install pymupdf Pillow pytesseract and system tesseract") from e
    doc = fitz.open(path)
    pages = []
    for page in doc:
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages.append(pytesseract.image_to_string(img))
    return "\n".join(pages).strip()

PARSERS: Dict[str, Callable[..., str]] = {
    "pymupdf": extract_text_pymupdf,
    "docx": extract_text_docx,
    "ocr": extract_text_ocr,
}
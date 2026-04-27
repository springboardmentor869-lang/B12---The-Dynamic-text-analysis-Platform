"""
parsers.py - minimal in-process document parsers.

This module provides simple text extraction utilities for different file types.
It defines a PARSERS dictionary mapping parser names to functions that:
    - Accept a file path as input
    - Return extracted text as a string

Supported Parsers:
1. pymupdf  : Extracts text from PDF files using PyMuPDF
2. docx     : Extracts text from DOCX files using python-docx
3. ocr      : Extracts text from scanned PDFs using OCR (Tesseract)

Required Libraries (only install if using that parser):
- pymupdf      : For reading and rendering PDF files
- python-docx  : For reading Microsoft Word (.docx) files
- pytesseract  : OCR engine wrapper for Python
- Pillow       : Image processing (required for OCR)
- Tesseract OCR must be installed on the system for OCR to work

Input:
- path (str): Path to the document file

Output:
- str: Extracted plain text from the document
"""

from typing import Callable, Dict
import fitz  # PyMuPDF
from docx import Document
import fitz
from PIL import Image
import pytesseract

# Extract text from a PDF file using PyMuPDF
def extract_text_pymupdf(path: str) -> str:

    doc = fitz.open(path)

    pages = []
    for p in doc:
        pages.append(p.get_text("text") or "")
    return "\n".join(pages).strip()

# Extract text from a DOCX file using python-docx.
def extract_text_docx(path: str) -> str:
    
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs).strip()

# Extract text from scanned PDFs using OCR (Tesseract).
def extract_text_ocr(path: str, dpi: int = 200) -> str:
    
    doc = fitz.open(path)

    pages = []
    for page in doc:
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0) # Set resolution for better OCR accuracy
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages.append(pytesseract.image_to_string(img))
    return "\n".join(pages).strip()

# Dictionary mapping parser names to extraction functions
PARSERS: Dict[str, Callable[..., str]] = {
    "pymupdf": extract_text_pymupdf,
    "docx": extract_text_docx,
    "ocr": extract_text_ocr,
}
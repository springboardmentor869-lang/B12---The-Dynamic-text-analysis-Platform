import os
import fitz  # PyMuPDF
import pdfplumber
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
from jiwer import wer


# ---------------- CONFIG ----------------
PDF_FILES = [
    "Agata Christie Woman Of Mystery-www.learnenglishteam.com.pdf",
    "American Customs And Traditions-www.learnenglishteam.com.pdf",
    "Spider-Man-elementary-pdf-story-learnenglishteam.com.pdf"
]
# --------------------------------------


def clean_text(text):
    if not text:
        return ""
    return " ".join(text.lower().split())


# ---------------- PARSERS ----------------
def parse_pdfplumber(pdf):
    text = ""
    with pdfplumber.open(pdf) as p:
        for page in p.pages:
            text += page.extract_text() or ""
    return clean_text(text)


def parse_pdfminer(pdf):
    return clean_text(extract_text(pdf))


def parse_pypdf2(pdf):
    text = ""
    reader = PdfReader(pdf)
    for page in reader.pages:
        text += page.extract_text() or ""
    return clean_text(text)


def parse_pymupdf(pdf):
    text = ""
    doc = fitz.open(pdf)
    for page in doc:
        text += page.get_text()
    return clean_text(text)
# ---------------------------------------


parsers = {
    "PDFPlumber": parse_pdfplumber,
    "PDFMiner": parse_pdfminer,
    "PyPDF2": parse_pypdf2,
    "PyMuPDF": parse_pymupdf
}


# ---------------- PROCESS ----------------
print("\nFILES SEEN BY PYTHON:")
for f in os.listdir("."):
    print(repr(f))
for pdf in PDF_FILES:
    print(f"\nProcessing PDF: {pdf}")

    ref_file = pdf.replace(".pdf", "_ref.txt")

    if not os.path.isfile(ref_file):
        print(f"❌ Reference file missing: {ref_file}")
        continue

    with open(ref_file, "r", encoding="utf-8") as f:
        reference_text = clean_text(f.read())

    wer_results = {}

    for lib, parser_func in parsers.items():
        try:
            extracted_text = parser_func(pdf)

            if extracted_text.strip():
                score = wer(reference_text, extracted_text)
                wer_results[lib] = score
                print(f"{lib} WER: {score}")
            else:
                wer_results[lib] = float("inf")
                print(f"{lib} WER: extraction failed")

        except Exception as e:
            wer_results[lib] = float("inf")
            print(f"{lib} ERROR: {e}")

    # -------- CONCLUSION FOR THIS PDF --------
    best_library = min(wer_results, key=wer_results.get)
    best_wer = wer_results[best_library]

    print("\n✅ Best parser for this PDF:")
    print(f"   Library : {best_library}")
    print(f"   WER     : {best_wer}")
# -----------------------------------------
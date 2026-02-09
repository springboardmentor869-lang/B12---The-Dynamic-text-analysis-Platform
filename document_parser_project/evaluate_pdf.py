import pdfplumber
import fitz
from jiwer import wer

pdf_path = "pdfs/cinderella.pdf"
truth_path = "ground_truth/cinderella.txt"

with open(truth_path, "r", encoding="utf-8") as f:
    ground_truth = f.read()

# pdfplumber
text1 = ""
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text1 += page.extract_text() or ""

wer_pdfplumber = wer(ground_truth, text1)

# PyMuPDF
doc = fitz.open(pdf_path)
text2 = ""
for page in doc:
    text2 += page.get_text()

wer_pymupdf = wer(ground_truth, text2)

print("pdfplumber WER:", wer_pdfplumber)
print("PyMuPDF WER:", wer_pymupdf)

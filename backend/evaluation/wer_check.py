from jiwer import wer
import re

# ---------- Text Normalization ----------
def normalize(text):
    text = text.lower()
    text = text.replace('\n', ' ')      # keep hyphens (don’t split)
    text = re.sub(r'[^a-z\- ]', '', text)  # keep hyphens
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ---------- Load Reference Text ----------
with open("../data/reference.txt", "r", encoding="utf-8") as f:
    reference_text = normalize(f.read())

# ---------- WER Calculation Function ----------
def calculate_wer(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        extracted_text = normalize(f.read())
    return wer(reference_text, extracted_text)

# ---------- Compute WER for Each Parser ----------
wer_pypdf2 = calculate_wer("pypdf2.txt")
wer_pdfplumber = calculate_wer("pdfplumber.txt")
wer_pymupdf = calculate_wer("pymupdf.txt")

# ---------- Display Results ----------
print("PDF Parser Evaluation using Word Error Rate (WER)")
print("-------------------------------------------------")
print(f"PyPDF2 WER     : {wer_pypdf2}")
print(f"pdfplumber WER : {wer_pdfplumber}")
print(f"PyMuPDF WER    : {wer_pymupdf}")

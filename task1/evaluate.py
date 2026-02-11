import os
import re
from jiwer import wer
from parsers import pdfplumber_parser, pypdf2_parser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PDF_PATH = os.path.join(BASE_DIR, "pdfs", "sample.pdf")
GROUND_TRUTH_PATH = os.path.join(BASE_DIR, "ground_truth", "sample.txt")


def clean_text(text):
    text = text.lower()
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_ground_truth(path):
    with open(path, "r", encoding="latin-1") as f:
        return f.read()


def run_evaluation():
    gt = clean_text(load_ground_truth(GROUND_TRUTH_PATH))

    pdfplumber_text = clean_text(pdfplumber_parser.extract_text(PDF_PATH))
    pypdf2_text = clean_text(pypdf2_parser.extract_text(PDF_PATH))

    pdfplumber_wer = wer(gt, pdfplumber_text)
    pypdf2_wer = wer(gt, pypdf2_text)

    print("\nPDF Parser Comparison\n")
    print(f"pdfplumber WER : {pdfplumber_wer:.4f}")
    print(f"PyPDF2 WER     : {pypdf2_wer:.4f}")

    if pdfplumber_wer < pypdf2_wer:
        print("\nBest Parser: pdfplumber")
    else:
        print("\nBest Parser: PyPDF2")


if __name__ == "__main__":
    run_evaluation()

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import re
from jiwer import wer

from parsers import pdfplumber_parser
from parsers import pypdf2_parser
from parsers import pymupdf_parser


PDF_PATH = "../../data/pdf_samples/sample1.pdf"
GROUND_TRUTH_PATH = "../../data/ground_truth/sample1.txt"

def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def load_ground_truth(path):
    with open(path, "r", encoding="utf-8") as f:
        return clean_text(f.read())

def run_evaluation():
    ground_truth = load_ground_truth(GROUND_TRUTH_PATH)

    parsers = {
        "PDFPlumber": pdfplumber_parser.extract_text,
        "PyPDF2": pypdf2_parser.extract_text,
        "PyMuPDF": pymupdf_parser.extract_text,
    }

    results = {}

    for name, extractor in parsers.items():
        extracted = clean_text(extractor(PDF_PATH))
        results[name] = wer(ground_truth, extracted)

    print("\nPDF Parser Evaluation Results\n")

    for name, score in results.items():
        print(f"{name}: {score:.4f}")

    best = min(results, key=results.get)
    print(f"\nBest Parser: {best}")

if __name__ == "__main__":
    run_evaluation()
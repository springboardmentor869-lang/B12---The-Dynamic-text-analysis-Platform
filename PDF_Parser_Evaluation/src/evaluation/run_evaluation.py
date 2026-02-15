import sys
import os
import re
from jiwer import wer

# This helps the script find the 'parsers' folder
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from parsers import pdfplumber_parser
from parsers import pypdf2_parser
from parsers import pymupdf_parser

# Paths to your files
# Updated paths to point correctly from the main project folder
PDF_PATH = "data/pdf_samples/sample1.pdf"
GROUND_TRUTH_PATH = "data/ground_truth/sample1.txt"

def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def load_ground_truth(path):
    with open(path, "r", encoding="utf-8") as f:
        return clean_text(f.read())

def run_evaluation():
    # Check if files exist
    if not os.path.exists(PDF_PATH) or not os.path.exists(GROUND_TRUTH_PATH):
        print(f"Error: Make sure {PDF_PATH} and {GROUND_TRUTH_PATH} exist!")
        return

    ground_truth = load_ground_truth(GROUND_TRUTH_PATH)

    parsers = {
        "PDFPlumber": pdfplumber_parser.extract_text,
        "PyPDF2": pypdf2_parser.extract_text,
        "PyMuPDF": pymupdf_parser.extract_text,
    }

    results = {}

    print("Running evaluations... please wait.")

    for name, extractor in parsers.items():
        try:
            extracted = clean_text(extractor(PDF_PATH))
            results[name] = wer(ground_truth, extracted)
        except Exception as e:
            print(f"Error running {name}: {e}")

    print("\nPDF Parser Evaluation Results\n")
    for name, score in results.items():
        print(f"{name}: {score:.4f}")

    if results:
        best = min(results, key=results.get)
        print(f"\nBest Parser: {best}")

if __name__ == "__main__":
    run_evaluation()
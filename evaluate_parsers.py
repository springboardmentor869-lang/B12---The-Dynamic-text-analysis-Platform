#!/usr/bin/env python3
"""
Evaluate selected parsers on data/pdfs and data/docx using WER.
No config.py required: choose parsers via CLI args (--pdf-parsers, --docx-parsers).
"""
import os
import argparse
import pandas as pd
from jiwer import wer, Compose, RemovePunctuation, ToLowerCase, RemoveMultipleSpaces
from parsers import PARSERS

DATA_DIR = "data"
PDFS_DIR = os.path.join(DATA_DIR, "pdfs")
DOCX_DIR = os.path.join(DATA_DIR, "docx")
GROUND_DIR = os.path.join(DATA_DIR, "ground_truth")
RESULTS_DIR = "results"
EXTRACTED_DIR = os.path.join(RESULTS_DIR, "extracted")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(EXTRACTED_DIR, exist_ok=True)

# Normalization for WER
TRANSFORM = Compose([ToLowerCase(), RemovePunctuation(), RemoveMultipleSpaces()])

def load_ground(basename):
    path = os.path.join(GROUND_DIR, basename + ".txt")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf8") as f:
        return f.read()

def collect_files():
    pdfs = [os.path.join(PDFS_DIR, f) for f in os.listdir(PDFS_DIR) if f.lower().endswith(".pdf")] if os.path.isdir(PDFS_DIR) else []
    docx = [os.path.join(DOCX_DIR, f) for f in os.listdir(DOCX_DIR) if f.lower().endswith(".docx")] if os.path.isdir(DOCX_DIR) else []
    return pdfs, docx

def evaluate_files(paths, parser_name):
    rows = []
    parser_callable = PARSERS.get(parser_name)
    if parser_callable is None:
        print(f"[WARN] Parser '{parser_name}' not available; skipping.")
        return rows
    for path in paths:
        basename = os.path.splitext(os.path.basename(path))[0]
        reference = load_ground(basename)
        if reference is None:
            print(f"[WARN] Ground truth missing for {basename}; skipping.")
            continue
        print(f"[{parser_name}] Extracting {basename} ...")
        try:
            text = parser_callable(path)
        except Exception as e:
            print(f"[ERROR] Parser {parser_name} failed on {basename}: {e}")
            text = ""
        # save extracted text for inspection
        out_dir = os.path.join(EXTRACTED_DIR, parser_name)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, basename + ".txt"), "w", encoding="utf8") as f:
            f.write(text)
        ref_norm = TRANSFORM(reference)
        hyp_norm = TRANSFORM(text)
        score = wer(ref_norm, hyp_norm)
        rows.append({"file": basename, "parser": parser_name, "wer": score})
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-parsers", nargs="*", help="List of parsers to run for PDFs (default: pymupdf ocr)")
    ap.add_argument("--docx-parsers", nargs="*", help="List of parsers to run for DOCX (default: docx)")
    args = ap.parse_args()

    pdf_parsers = args.pdf_parsers or ["pymupdf", "ocr"]
    docx_parsers = args.docx_parsers or ["docx"]

    pdfs, docx_files = collect_files()
    if not pdfs and not docx_files:
        print("No input files found in data/pdfs or data/docx")
        return

    all_rows = []
    # PDF parsers
    if pdfs:
        for p in pdf_parsers:
            all_rows.extend(evaluate_files(pdfs, p))
    # DOCX parsers
    if docx_files:
        for p in docx_parsers:
            all_rows.extend(evaluate_files(docx_files, p))

    df = pd.DataFrame(all_rows)
    csv_path = os.path.join(RESULTS_DIR, "wer_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"Results written to {csv_path}")
    if not df.empty:
        print("\nMean WER per parser:")
        print(df.groupby("parser")["wer"].mean().sort_values())
if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
evaluate_parsers.py - simple WER-based parser evaluation.

This script evaluates different document parsers using Word Error Rate (WER).
It:
    - Reads PDFs from a specified directory
    - Extracts text using each parser in parsers.PARSERS
    - Compares extracted text against reference .txt files
    - Computes Word Error Rate (WER)
    - Writes results to a CSV file

Usage:
python evaluate_parsers.py 
    --pdfs-dir data/pdfs 
    --refs-dir data/ground_truth 
    --out results/eval.csv

Expected Structure:
- For each <name>.pdf in pdfs_dir
  there must be a corresponding <name>.txt in refs_dir

Required Libraries:
- os        : File system operations
- csv       : Writing evaluation results
- argparse  : CLI argument parsing
- parsers   : Access available extraction methods
- convert_document - Text extraction utility

Input:
- Directory of PDF files
- Directory of reference TXT files

Output:
- CSV file with columns:
    pdf | parser | wer | error
"""

import os
import csv
import argparse

from parsers import PARSERS
from convert_document import extract_with_fallback

# Compute Word Error Rate (WER) between reference and hypothesis text.
def wer(ref: str, hyp: str) -> float:
    
    # Split texts into word tokens
    r = ref.split()
    h = hyp.split()
    n = len(r)
    
    # Initialize dynamic programming matrix
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    
    # Base case initialization
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j
    
    # Compute edit distance using dynamic programming matrix
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            cost = 0 if r[i-1] == h[j-1] else 1
            d[i][j] = min(
                d[i-1][j] + 1,      # deletion
                d[i][j-1] + 1,      # insertion
                d[i-1][j-1] + cost  # substitution
                )
    
    edits = d[len(r)][len(h)]
    
    return (edits / n) if n > 0 else (0.0 if edits == 0 else 1.0)

# Evaluate all parsers on given PDFs and write WER results to CSV
def evaluate(pdfs_dir: str, refs_dir: str, out_csv: str):
    
    # Get sorted list of PDF files
    pdfs = sorted([f for f in os.listdir(pdfs_dir) if f.lower().endswith(".pdf")])
    rows = []

    for pdf in pdfs:
        base = os.path.splitext(pdf)[0]
        refpath = os.path.join(refs_dir, base + ".txt")

        # Skip if no reference file exists
        if not os.path.exists(refpath):
            print(f"[SKIP] No reference for {pdf}")
            continue

        # Load reference text
        with open(refpath, "r", encoding="utf8", errors="replace") as rf:
            ref = rf.read().strip()
        
        path = os.path.join(pdfs_dir, pdf)
        
        # Evaluate each parser
        for parser_name in PARSERS.keys():
            try:
                hyp = extract_with_fallback(path, parser=parser_name)
            except Exception as e:
                print(f"[ERROR] {pdf} with {parser_name}: {e}")
                rows.append({"pdf": pdf, "parser": parser_name, "wer": "", "error": str(e)})
                continue

            score = wer(ref, hyp)
            print(f"{pdf} | {parser_name} -> WER={score:.4f}")

            rows.append({
                "pdf": pdf,
                "parser": parser_name,
                "wer": f"{score:.4f}", "error": ""
            })

    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)

    # Write results to CSV
    with open(out_csv, "w", newline="", encoding="utf8") as cf:
        writer = csv.DictWriter(cf, fieldnames=["pdf", "parser", "wer", "error"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    
    print(f"Wrote evaluation CSV to {out_csv}")

# CLI entry point for parser evaluation.
def main():
    
    # Configure CLI arguments
    ap = argparse.ArgumentParser(prog="evaluate_parsers.py")
    ap.add_argument("--pdfs-dir", default="data/pdfs")
    ap.add_argument("--refs-dir", default="data/ground_truth")
    ap.add_argument("--out", default="results/eval_parsers.csv")

    args = ap.parse_args()

    evaluate(args.pdfs_dir, args.refs_dir, args.out)

if __name__ == "__main__":
    main()
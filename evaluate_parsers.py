import os
import csv
from jiwer import wer, Compose, RemovePunctuation, ToLowerCase, RemoveMultipleSpaces
import argparse
import pandas as pd
from parsers import PARSERS

DATA_DIR = "data"
PDFS_DIR = os.path.join(DATA_DIR, "pdfs")
DOCX_DIR = os.path.join(DATA_DIR, "docx")
GROUND_DIR = os.path.join(DATA_DIR, "ground_truth")
RESULTS_DIR = "results"
EXTRACTED_DIR = os.path.join(RESULTS_DIR, "extracted")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(EXTRACTED_DIR, exist_ok=True)

# Normalization pipeline for WER
TRANSFORM = Compose([ToLowerCase(), RemovePunctuation(), RemoveMultipleSpaces()])

def load_ground(basename):
    path = os.path.join(GROUND_DIR, basename + ".txt")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf8") as f:
        return f.read()

def evaluate(paths, parser_name, parser_callable):
    rows = []
    for path in paths:
        basename = os.path.splitext(os.path.basename(path))[0]
        ref = load_ground(basename)
        if ref is None:
            print(f"[WARN] No ground truth for {basename}, skipping.")
            continue
        print(f"[{parser_name}] processing {basename}")
        try:
            text = parser_callable(path)
        except Exception as e:
            print(f"[ERROR] parser failed: {e}")
            text = ""
        # optional: save extracted text
        out_dir = os.path.join(EXTRACTED_DIR, parser_name)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, basename + ".txt"), "w", encoding="utf8") as f:
            f.write(text)
        # Normalize reference and hypothesis using TRANSFORM, then compute WER
        ref_norm = TRANSFORM(ref) if ref is not None else ""
        hyp_norm = TRANSFORM(text) if text is not None else ""
        score = wer(ref_norm, hyp_norm)
        rows.append({"file": basename, "parser": parser_name, "wer": score})
    return rows

def collect_files():
    pdfs = [os.path.join(PDFS_DIR, f) for f in os.listdir(PDFS_DIR) if f.lower().endswith(".pdf")] if os.path.isdir(PDFS_DIR) else []
    docx = [os.path.join(DOCX_DIR, f) for f in os.listdir(DOCX_DIR) if f.lower().endswith(".docx")] if os.path.isdir(DOCX_DIR) else []
    return pdfs, docx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parsers", nargs="*", help="limit parsers to run")
    args = ap.parse_args()

    pdfs, docx = collect_files()
    if not pdfs and not docx:
        print("No input files found in data/pdfs or data/docx")
        return

    selected = args.parsers or list(PARSERS.keys())
    all_rows = []
    for p in selected:
        if p not in PARSERS:
            print(f"[WARN] unknown parser {p}")
            continue
        callable_ = PARSERS[p]
        if p == "docx":
            rows = evaluate(docx, p, callable_)
        else:
            rows = evaluate(pdfs, p, callable_)
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    csv_path = os.path.join(RESULTS_DIR, "wer_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"Results written to {csv_path}")
    if not df.empty:
        print(df.groupby("parser")["wer"].mean().sort_values())
if __name__ == "__main__":
    main()
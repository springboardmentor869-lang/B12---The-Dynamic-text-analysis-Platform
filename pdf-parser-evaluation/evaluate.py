import os
import pandas as pd
from jiwer import wer
from extractors import (
    extract_pymupdf,
    extract_pdfplumber,
    extract_pypdf2,
    extract_pdfminer
)

DATASET_DIR = "dataset"

libraries = {
    "pymupdf": extract_pymupdf,
    "pdfplumber": extract_pdfplumber,
    "pypdf2": extract_pypdf2,
    "pdfminer": extract_pdfminer
}

results = []

for file in os.listdir(DATASET_DIR):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(DATASET_DIR, file)
        gt_path = os.path.join(DATASET_DIR, file.replace(".pdf", "_gt.txt"))

        if not os.path.exists(gt_path):
            continue

        with open(gt_path, "r", encoding="utf-8") as f:
            ground_truth = f.read()

        for lib_name, extractor in libraries.items():
            try:
                prediction = extractor(pdf_path)
                error = wer(ground_truth, prediction)

                results.append({
                    "PDF": file,
                    "Library": lib_name,
                    "WER": error
                })

                print(f"{file} - {lib_name}: {error}")

            except Exception as e:
                print(f"Error in {lib_name} for {file}: {e}")

df = pd.DataFrame(results)
df.to_csv("results.csv", index=False)

print("\nEvaluation Complete!")
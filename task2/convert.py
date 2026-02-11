import os
import pdfplumber
from docx import Document

INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

for file in os.listdir(INPUT_DIR):
    input_path = os.path.join(INPUT_DIR, file)
    name, ext = os.path.splitext(file)

    if ext.lower() == ".pdf":
        text = extract_pdf(input_path)
        suffix = "_pdf"
    elif ext.lower() == ".docx":
        text = extract_docx(input_path)
        suffix = "_docx"
    else:
        continue

    output_path = os.path.join(OUTPUT_DIR, name + suffix + ".txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Converted {file} → {output_path}")
 
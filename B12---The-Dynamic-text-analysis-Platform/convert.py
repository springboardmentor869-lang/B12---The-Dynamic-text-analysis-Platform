import os
import fitz  # PyMuPDF
from docx import Document

INPUT_DIR = "../input_docs"
OUTPUT_DIR = "../output_docs"
OUTPUT_FORMAT = "txt"   # choose "txt" or "md"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------- PDF to text --------
def pdf_to_text(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text

# -------- DOCX to text --------
def docx_to_text(file_path):
    document = Document(file_path)
    text = ""
    for para in document.paragraphs:
        text += para.text + "\n"
    return text

# -------- Save output --------
def save_output(filename, text):
    name = os.path.splitext(filename)[0]
    output_path = os.path.join(OUTPUT_DIR, f"{name}.{OUTPUT_FORMAT}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved: {output_path}")

# -------- Main --------
for file in os.listdir(INPUT_DIR):
    file_path = os.path.join(INPUT_DIR, file)

    if file.endswith(".pdf"):
        text = pdf_to_text(file_path)
        save_output(file, text)

    elif file.endswith(".docx"):
        text = docx_to_text(file_path)
        save_output(file, text)

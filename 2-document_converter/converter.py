import os
import pdfplumber
from docx import Document

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def save_text(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

input_folder = "input_files"
output_folder = "output_files"

for file in os.listdir(input_folder):
    file_path = os.path.join(input_folder, file)

    if file.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
        output_name = file.replace(".pdf", ".txt")

    elif file.endswith(".docx"):
        text = extract_text_from_docx(file_path)
        output_name = file.replace(".docx", ".md")

    else:
        continue

    output_path = os.path.join(output_folder, output_name)
    save_text(text, output_path)

print("Conversion completed successfully")

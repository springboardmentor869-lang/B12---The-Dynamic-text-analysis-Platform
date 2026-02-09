import pdfplumber
from docx import Document
import os

def pdf_to_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def docx_to_text(path):
    doc = Document(path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def convert(file_path, output_format="txt"):
    name, ext = os.path.splitext(file_path)

    if ext == ".pdf":
        text = pdf_to_text(file_path)
    elif ext == ".docx":
        text = docx_to_text(file_path)
    else:
        print("Unsupported file format")
        return

    output_path = "outputs/" + os.path.basename(name) + "." + output_format

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("File saved to", output_path)
if __name__ == "__main__":
    convert("pdfs/cinderella.pdf", "txt")


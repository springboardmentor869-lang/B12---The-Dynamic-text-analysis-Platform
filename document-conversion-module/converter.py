import os
import pymupdf  # for PDF
from docx import Document  # for DOCX


INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"


def extract_text_from_pdf(file_path):
    text = ""
    with pymupdf.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def save_output(text, original_filename, output_format="txt"):
    base_name = os.path.splitext(original_filename)[0]
    output_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.{output_format}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"✅ Saved: {output_path}")


def process_files(output_format="txt"):
    for filename in os.listdir(INPUT_FOLDER):
        file_path = os.path.join(INPUT_FOLDER, filename)

        if filename.endswith(".pdf"):
            print(f"Processing PDF: {filename}")
            text = extract_text_from_pdf(file_path)

        elif filename.endswith(".docx"):
            print(f"Processing DOCX: {filename}")
            text = extract_text_from_docx(file_path)

        else:
            continue

        save_output(text, filename, output_format)


if __name__ == "__main__":
    process_files("md")   # Change to "md" if needed
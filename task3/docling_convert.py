import os
from docling.document_converter import DocumentConverter

INPUT_DIR = "input_docs"
OUTPUT_DIR = "output_docs_docling"

os.makedirs(OUTPUT_DIR, exist_ok=True)

converter = DocumentConverter()

for file in os.listdir(INPUT_DIR):
    if file.lower().endswith((".pdf", ".docx")):
        file_path = os.path.join(INPUT_DIR, file)
        print(f"Processing: {file}")

        result = converter.convert(file_path)

        name = os.path.splitext(file)[0]
        out_path = os.path.join(OUTPUT_DIR, name + ".md")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(result.document.export_to_markdown())

        print(f"Saved: {out_path}")

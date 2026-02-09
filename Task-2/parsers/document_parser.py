import os
import fitz  # PyMuPDF
from docx import Document

class DocumentParser:
    """
    Parser module for Task 2:
    - Extracts text from PDF and DOCX
    - Saves as .txt or .md
    """

    def __init__(self):
        pass

    # ---------- PDF extraction ----------
    def parse_pdf(self, pdf_path):
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    # ---------- DOCX extraction ----------
    def parse_docx(self, docx_path):
        text = ""
        doc = Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

    # ---------- Save extracted text ----------
    def save_text(self, text, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[INFO] Saved extracted text to {output_path}")

    # ---------- Automatic parser ----------
    def parse_and_save(self, input_path, output_path=None):
        ext = os.path.splitext(input_path)[1].lower()

        if ext == ".pdf":
            text = self.parse_pdf(input_path)
        elif ext == ".docx":
            text = self.parse_docx(input_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        # Default output path if not provided
        if output_path is None:
            base = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join("../../output", base + ".txt")

        self.save_text(text, output_path)
        return output_path

    # ---------- Batch processing ----------
    def batch_process_folder(self, input_folder, output_folder="../../output"):
        os.makedirs(output_folder, exist_ok=True)
        for filename in os.listdir(input_folder):
            if filename.lower().endswith((".pdf", ".docx")):
                input_path = os.path.join(input_folder, filename)
                base = os.path.splitext(filename)[0]
                output_path = os.path.join(output_folder, base + ".txt")
                self.parse_and_save(input_path, output_path)

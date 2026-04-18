import os
import fitz  # PyMuPDF
from docx import Document


class DocumentParser:

    # ==========================================
    # PDF → TEXT
    # ==========================================
    def parse_pdf(self, pdf_path):
        try:
            text = ""
            doc = fitz.open(pdf_path)

            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"

            doc.close()
            return text.strip()

        except Exception as e:
            print(f"[PDF Parse Error] {e}")
            return ""


    # ==========================================
    # DOCX → TEXT
    # ==========================================
    def parse_docx(self, docx_path):
        try:
            text = ""
            doc = Document(docx_path)

            for para in doc.paragraphs:
                if para.text.strip():
                    text += para.text.strip() + "\n"

            return text.strip()

        except Exception as e:
            print(f"[DOCX Parse Error] {e}")
            return ""


    # ==========================================
    # SAVE FILE (.md)
    # ==========================================
    def save_markdown(self, text, output_path):
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            paragraphs = text.split("\n")
            md_lines = ["# Converted Document\n"]

            for para in paragraphs:
                para = para.strip()
                if para:
                    md_lines.append(f"{para}\n")

            markdown_text = "\n".join(md_lines)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_text)

            print(f"[INFO] Saved → {output_path}")

        except Exception as e:
            print(f"[Markdown Save Error] {e}")


    # ==========================================
    # MAIN FUNCTION
    # ==========================================
    def parse_and_save(self, input_path, output_path=None):
        ext = os.path.splitext(input_path)[1].lower()

        if ext == ".pdf":
            text = self.parse_pdf(input_path)

        elif ext == ".docx":
            text = self.parse_docx(input_path)

        else:
            raise ValueError(f"Unsupported file type: {ext}")

        if not text.strip():
            raise ValueError("No text extracted from document.")

        if output_path is None:
            base = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join("markdown_outputs", base + ".md")

        self.save_markdown(text, output_path)

        return output_path
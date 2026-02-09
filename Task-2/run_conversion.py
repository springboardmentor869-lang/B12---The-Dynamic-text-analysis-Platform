import os
from parsers.document_parser import DocumentParser

def run_document_conversion():
    parser = DocumentParser()

    # -------- Single file examples --------
    pdf_file = "data/pdfs/sample1.pdf"
    parser.parse_and_save(pdf_file, "output/sample1.txt")

    # If you have DOCX files
    docx_file = "data/docs/sample1.docx"
    if os.path.exists(docx_file):
        parser.parse_and_save(docx_file, "output/sample1.md")

    # -------- Batch process folders --------
    pdf_folder = "data/pdfs"
    parser.batch_process_folder(pdf_folder, output_folder="output")

    # Optional: batch process DOCX
    docx_folder = "data/docs"
    if os.path.exists(docx_folder):
        parser.batch_process_folder(docx_folder, output_folder="output")

if __name__ == "__main__":
    run_document_conversion()

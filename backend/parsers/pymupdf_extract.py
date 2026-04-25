import fitz  # PyMuPDF

def extract_text_pymupdf(file_path):
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print("PyMuPDF error:", e)
    return text
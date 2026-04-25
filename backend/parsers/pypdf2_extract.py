from PyPDF2 import PdfReader

def extract_text_pypdf2(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print("PyPDF2 error:", e)
    return text
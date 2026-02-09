import fitz          # PDF parser (PyMuPDF)
import docx          # DOCX parser
import pandas as pd  # CSV parser

def read_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def read_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def read_docx(path):
    document = docx.Document(path)
    return "\n".join(p.text for p in document.paragraphs)

def read_csv(path):
    df = pd.read_csv(path)
    return " ".join(df.iloc[:, 0].astype(str))

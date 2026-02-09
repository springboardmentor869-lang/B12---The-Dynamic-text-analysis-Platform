import pdfplumber

text = ""

with pdfplumber.open("sample.pdf") as pdf:
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

with open("../evaluation/pdfplumber.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("pdfplumber done")

import PyPDF2

text = ""

with open("sample.pdf", "rb") as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

with open("../evaluation/pypdf2.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("PyPDF2 done")

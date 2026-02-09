import PyPDF2
openPDF = open("Sunflower.pdf", "rb")
pdfRead = PyPDF2.PdfReader(openPDF)
print(len(pdfRead.pages))
print(pdfRead.is_encrypted)
print(pdfRead.metadata)
print(pdfRead.pages[0].extract_text())
for i in range(len(pdfRead.pages)):
    page = pdfRead.pages[i]
    text = page.extract_text()
    print(f"\n--- Page {i+1} ---\n")
    print(text)
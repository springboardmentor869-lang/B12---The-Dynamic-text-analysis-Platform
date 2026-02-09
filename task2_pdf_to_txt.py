import os
import pdfplumber


PDF_FILES = [
    "Agata Christie Woman Of Mystery-www.learnenglishteam.com.pdf",
    "American Customs And Traditions-www.learnenglishteam.com.pdf",
    "Spider-Man-elementary-pdf-story-learnenglishteam.com.pdf"
]

OUTPUT_DIR = "output_txt"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


for pdf_file in PDF_FILES:
    if not os.path.exists(pdf_file):
        print(f"❌ File not found: {pdf_file}")
        continue

    print(f"Processing: {pdf_file}")

    extracted_text = extract_text_from_pdf(pdf_file)

    output_file = os.path.join(
        OUTPUT_DIR,
        pdf_file.replace(".pdf", ".txt")
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    print(f"✅ Saved TXT: {output_file}")
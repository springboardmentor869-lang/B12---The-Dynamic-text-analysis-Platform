import fitz  # PyMuPDF


def convert_pdf_to_markdown(file_path):
    """
    Convert PDF to Markdown text
    """
    doc = fitz.open(file_path)
    markdown_text = ""

    for page_num, page in enumerate(doc):
        text = page.get_text("text")

        markdown_text += f"\n\n## Page {page_num + 1}\n\n"
        markdown_text += text

    doc.close()
    return markdown_text


# ✅ THIS PART MAKES IT RUN
if __name__ == "__main__":
    file_path = "sample.pdf"  # Make sure this file exists in same folder

    try:
        result = convert_pdf_to_markdown(file_path)
        print("\n✅ MARKDOWN OUTPUT:\n")
        print(result)

    except Exception as e:
        print("❌ Error:", str(e))
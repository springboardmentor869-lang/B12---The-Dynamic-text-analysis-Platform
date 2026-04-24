import fitz
import docx
import tempfile
from utils.file_handler import save_text_file


async def parse_document(content, filename):
    filename = filename.lower()

    if filename.endswith(".pdf"):
        text = await parse_pdf(content)

    elif filename.endswith(".docx"):
        text = await parse_docx(content)

    else:
        raise ValueError("Unsupported file type")

    path = save_text_file(text, filename)
    return text, path


async def parse_pdf(content):
    doc = fitz.open(stream=content, filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text()

    return text


async def parse_docx(content):
    # safe temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    doc = docx.Document(tmp_path)
    text = "\n".join([p.text for p in doc.paragraphs])

    return text
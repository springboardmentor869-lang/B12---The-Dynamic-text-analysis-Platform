import fitz


def load_pdf(file_path):

    doc = fitz.open(file_path)

    text = ""

    for page in doc:
        text += page.get_text()

    return text


def split_into_chunks(text, chunk_size=500):

    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(words[i:i + chunk_size])

        if chunk.strip():
            chunks.append(chunk)

    return chunks
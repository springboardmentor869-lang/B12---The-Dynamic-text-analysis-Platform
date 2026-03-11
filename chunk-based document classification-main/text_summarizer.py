import fitz
from transformers import pipeline


# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def load_pdf(file_path):

    doc = fitz.open(file_path)

    text = ""

    for page in doc:
        text += page.get_text()

    return text


def summarize_pdf(file_path):

    print(f"Loading PDF: {file_path}")

    text = load_pdf(file_path)

    print("Generating summary...")

    summary = summarizer(
        text,
        max_length=150,
        min_length=40,
        do_sample=False
    )

    return summary[0]["summary_text"]


if __name__ == "__main__":

    file_path = "documents/sample.pdf"

    result = summarize_pdf(file_path)

    print("\n==============================")
    print("PDF SUMMARY")
    print("==============================\n")

    print(result)
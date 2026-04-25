from transformers import pipeline

# Load once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    try:
        text = text[:2000]  # limit size
        result = summarizer(
            text,
            max_length=120,
            min_length=40,
            do_sample=False
        )
        return result[0]["summary_text"]
    except Exception as e:
        print("Summarization error:", e)
        return "Summary could not be generated."
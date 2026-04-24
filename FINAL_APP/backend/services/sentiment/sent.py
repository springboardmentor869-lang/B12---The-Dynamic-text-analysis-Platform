import nltk
from transformers import pipeline
import warnings

warnings.filterwarnings("ignore")

# Download tokenizer once
nltk.download('punkt', quiet=True)

MODEL_NAME = "ProsusAI/finbert"

# Lazy-loaded pipeline (prevents slow startup / crashes)
_sentiment_pipeline = None


def get_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=MODEL_NAME,
            tokenizer=MODEL_NAME
        )
    return _sentiment_pipeline


def analyze_sentiment(text: str, task_manager=None, task_id=None) -> dict:
    """
    Analyze sentiment of a document text.

    Args:
        text (str): Full document text

    Returns:
        dict: sentence-level + overall sentiment results
    """

    if task_manager and task_id:
        task_manager.update_progress(task_id, "Initializing sentiment models...", 10)

    pipe = get_pipeline()

    # Step 1: Sentence split
    sentences = nltk.sent_tokenize(text)

    results = []

    positive_count = 0
    negative_count = 0
    neutral_count = 0

    sentences_to_process = sentences[:50]

    if task_manager and task_id:
        task_manager.update_progress(task_id, f"Running sentiment analysis on {len(sentences_to_process)} sentences...", 20)

    # Step 2: Analyze batch using pipeline batching 
    # (Significantly faster than sequential loops)
    # Truncation is required to prevent "tensor size mismatch" errors with long paragraphs.
    outputs = pipe(sentences_to_process, batch_size=8, truncation=True, max_length=512)

    for sentence, output in zip(sentences_to_process, outputs):
        # Extract the dictionary depending on pipeline return format
        if type(output) is list:
            out_dict = output[0]
        else:
            out_dict = output

        label = out_dict["label"]
        score = float(out_dict["score"])

        label_lower = label.lower()

        if "positive" in label_lower:
            positive_count += 1
        elif "negative" in label_lower:
            negative_count += 1
        else:
            neutral_count += 1

        results.append({
            "sentence": sentence,
            "label": label,
            "score": score
        })

    # Step 3: Overall sentiment (majority voting)
    if positive_count > negative_count:
        overall_sentiment = "Positive"
    elif negative_count > positive_count:
        overall_sentiment = "Negative"
    else:
        overall_sentiment = "Neutral"

    # Step 4: Return structured output
    return {
        "sentence_results": results,
        "total_sentences": len(sentences),
        "positive": positive_count,
        "negative": negative_count,
        "neutral": neutral_count,
        "overall_sentiment": overall_sentiment
    }
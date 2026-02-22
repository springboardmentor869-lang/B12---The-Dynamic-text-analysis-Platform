import nltk
from transformers import pipeline
import warnings

warnings.filterwarnings("ignore")

# Download sentence tokenizer
nltk.download('punkt', quiet=True)

# Load FinBERT model
MODEL_NAME = "ProsusAI/finbert"

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME
)

def analyze_sentiment_from_document(file_path: str) -> dict:
    # Step 1: Read document
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Step 2: Split into sentences
    sentences = nltk.sent_tokenize(text)

    results = []
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    # Step 3: Sentence-wise analysis
    for sentence in sentences:
        result = sentiment_pipeline(sentence)[0]

        label = result["label"]
        score = float(result["score"])

        # Count sentiments
        if label.lower() == "positive":
            positive_count += 1
        elif label.lower() == "negative":
            negative_count += 1
        else:
            neutral_count += 1

        results.append({
            "sentence": sentence,
            "label": label,
            "score": score
        })

    # Step 4: Overall sentiment (Majority voting)
    if positive_count > negative_count:
        overall_sentiment = "Positive"
    elif negative_count > positive_count:
        overall_sentiment = "Negative"
    else:
        overall_sentiment = "Neutral"

    return {
        "sentence_results": results,
        "total_sentences": len(sentences),
        "positive": positive_count,
        "negative": negative_count,
        "neutral": neutral_count,
        "overall_sentiment": overall_sentiment
    }


# Example usage
if __name__ == "__main__":
    file_path = "input.md"   # Put your document file here
    output = analyze_sentiment_from_document(file_path)

     # Print only first 10 sentences
    for item in output["sentence_results"][:10]:
        print(f"\nSentence: {item['sentence']}")
        print(f"Sentiment: {item['label']}")
        print(f"Confidence: {item['score']:.4f}")

    print("\nSummary:")
    print(f"Total Sentences: {output['total_sentences']}")
    print(f"Positive: {output['positive']}")
    print(f"Negative: {output['negative']}")
    print(f"Neutral: {output['neutral']}")
    print(f"Overall Sentiment: {output['overall_sentiment']}")

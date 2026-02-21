from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

# Load model
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# Function definition (THIS WAS MISSING)
def analyze_document(text):

    sentences = sent_tokenize(text)

    positive = 0
    negative = 0
    neutral = 0

    results = []

    for sentence in sentences:
        result = sentiment_analyzer(sentence)[0]
        label = result['label']
        score = result['score']

        # Neutral condition
        if score < 0.60:
            final_label = "NEUTRAL"
            neutral += 1
        elif label == "POSITIVE":
            final_label = "POSITIVE"
            positive += 1
        else:
            final_label = "NEGATIVE"
            negative += 1

        results.append((sentence, final_label, round(score, 3)))

    # Overall sentiment
    if positive > negative:
        overall = "POSITIVE"
    elif negative > positive:
        overall = "NEGATIVE"
    else:
        overall = "NEUTRAL"

    return results, positive, negative, neutral, overall


if __name__ == "__main__":

    with open("sample.txt", "r", encoding="utf-8") as f:
        document = f.read()

    results, pos, neg, neu, overall = analyze_document(document)

    print("\nSentence-Level Sentiment:\n")

    for sentence, label, score in results:
        print(f"Sentence: {sentence}")
        print(f"Sentiment: {label}")
        print(f"Confidence Score: {score}")
        print("-" * 50)

    print("\nSummary:")
    print(f"Positive Sentences: {pos}")
    print(f"Negative Sentences: {neg}")
    print(f"Neutral Sentences: {neu}")
    print(f"Overall Document Sentiment: {overall}")
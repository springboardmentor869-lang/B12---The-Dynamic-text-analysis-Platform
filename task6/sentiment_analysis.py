import nltk
from transformers import pipeline
from pypdf import PdfReader
import warnings

warnings.filterwarnings("ignore")
nltk.download('punkt')
MODEL_NAME = "ProsusAI/finbert"

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME
)

def read_pdf(path):
    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + " "

    return text

def analyze_sentiment(text):

    sentences = nltk.sent_tokenize(text)

    results = []
    pos = neg = neu = 0

    for sentence in sentences:

        result = sentiment_pipeline(sentence)[0]

        label = result["label"].lower()
        score = float(result["score"])

        if label == "positive":
            pos += 1
        elif label == "negative":
            neg += 1
        else:
            neu += 1

        results.append({
            "sentence": sentence,
            "label": label,
            "score": score
        })

   
    if pos > neg and pos > neu:
        overall = "POSITIVE"
    elif neg > pos and neg > neu:
        overall = "NEGATIVE"
    else:
        overall = "NEUTRAL"

    return results, pos, neg, neu, overall


if __name__ == "__main__":

   
    text = read_pdf("repot.pdf")
    
    results, pos, neg, neu, overall = analyze_sentiment(text)

    print("\nSentence Level Sentiment:\n")

    for r in results:
        print("Sentence:", r["sentence"])
        print("Sentiment:", r["label"])
        print("Confidence:", round(r["score"], 4))
        print("-----------")

    print("\nSummary:")
    print("Positive sentences:", pos)
    print("Negative sentences:", neg)
    print("Neutral sentences:", neu)
    print("Overall Document Sentiment:", overall)

import nltk
from nltk.tokenize import sent_tokenize
from transformers import pipeline

# Download tokenizer (only first time)
nltk.download('punkt')

# 🔹 Load extracted PDF text (RAW text)
file_path = "../output_docs_docling/sentiment_input.md"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 🔹 Split into sentences
sentences = sent_tokenize(text)

# 🔹 Load 3-class sentiment model
classifier = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert"
)

positive = 0
negative = 0
neutral = 0
total_confidence = 0

print("\n=========== Sentence Level Sentiment ===========\n")

for sentence in sentences:
    result = classifier(sentence)[0]

    label = result["label"].lower()
    score = result["score"]

    total_confidence += score

    if label == "positive":
        sentiment = "POSITIVE"
        positive += 1
    elif label == "negative":
        sentiment = "NEGATIVE"
        negative += 1
    else:
        sentiment = "NEUTRAL"
        neutral += 1

    print(f"Sentence: {sentence}")
    print(f"Sentiment: {sentiment} | Confidence: {round(score, 3)}")
    print("-" * 70)

total_sentences = len(sentences)

# 🔹 Determine overall document sentiment
if positive > negative and positive > neutral:
    overall = "POSITIVE"
elif negative > positive and negative > neutral:
    overall = "NEGATIVE"
else:
    overall = "NEUTRAL"

avg_confidence = total_confidence / total_sentences

print("\n================ DOCUMENT SUMMARY ================")
print(f"Total Sentences : {total_sentences}")
print(f"Positive        : {positive}")
print(f"Negative        : {negative}")
print(f"Neutral         : {neutral}")
print(f"Average Confidence : {round(avg_confidence, 3)}")
print(f"Overall Document Sentiment : {overall}")

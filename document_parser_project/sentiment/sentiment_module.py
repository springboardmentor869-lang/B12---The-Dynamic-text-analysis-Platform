import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize

# Download required resources (only first time)
nltk.download('punkt')
nltk.download('vader_lexicon')

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Read document
with open("sample.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Split into sentences
sentences = sent_tokenize(text)

positive_count = 0
negative_count = 0
neutral_count = 0

print("\n----- Sentence Level Sentiment -----\n")

for sentence in sentences:
    score = sia.polarity_scores(sentence)
    compound_score = score['compound']

    if compound_score >= 0.05:
        sentiment = "Positive"
        positive_count += 1
    elif compound_score <= -0.05:
        sentiment = "Negative"
        negative_count += 1
    else:
        sentiment = "Neutral"
        neutral_count += 1

    print(f"Sentence: {sentence}")
    print(f"Sentiment: {sentiment}")
    print(f"Confidence Score: {compound_score}")
    print("--------------------------------------------------")

# Overall Document Sentiment
overall_score = sia.polarity_scores(text)
overall_compound = overall_score['compound']

if overall_compound >= 0.05:
    overall_sentiment = "Overall Positive"
elif overall_compound <= -0.05:
    overall_sentiment = "Overall Negative"
else:
    overall_sentiment = "Overall Neutral"

print("\n===== Summary =====")
print(f"Total Sentences: {len(sentences)}")
print(f"Positive Sentences: {positive_count}")
print(f"Negative Sentences: {negative_count}")
print(f"Neutral Sentences: {neutral_count}")
print(f"\nOverall Document Sentiment: {overall_sentiment}")
print(f"Overall Confidence Score: {overall_compound}")
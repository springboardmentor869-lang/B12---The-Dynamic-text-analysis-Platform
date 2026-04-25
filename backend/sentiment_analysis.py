import re
from transformers import pipeline

# =====================================================
# LOAD MODEL ONCE
# =====================================================

classifier = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert"
)

# =====================================================
# SPLIT TEXT INTO SENTENCES
# =====================================================

def split_into_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]

# =====================================================
# MAIN FUNCTION
# =====================================================

def analyze_sentiment(text):
    sentences = split_into_sentences(text)

    if not sentences:
        return {
            "overall_sentiment": "NEUTRAL",
            "average_confidence": 0.0,
            "total_sentences": 0,
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "sentence_level": []
        }

    positive = 0
    negative = 0
    neutral = 0
    total_confidence = 0
    sentence_level = []

    MAX_SENTENCES = 40

    for sentence in sentences[:MAX_SENTENCES]:
        try:
            result = classifier(sentence[:512])[0]

            label = result["label"].lower()
            score = float(result["score"])
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

            sentence_level.append({
                "sentence": sentence,
                "label": sentiment,
                "confidence": round(score, 4)
            })

        except Exception as e:
            print("Sentiment error:", e)
            neutral += 1
            sentence_level.append({
                "sentence": sentence,
                "label": "NEUTRAL",
                "confidence": 0.0
            })

    total_sentences = len(sentence_level)

    if positive > negative and positive > neutral:
        overall = "POSITIVE"
    elif negative > positive and negative > neutral:
        overall = "NEGATIVE"
    else:
        overall = "NEUTRAL"

    avg_confidence = total_confidence / total_sentences if total_sentences > 0 else 0

    return {
        "overall_sentiment": overall,
        "average_confidence": round(avg_confidence, 4),
        "total_sentences": total_sentences,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "sentence_level": sentence_level
    }
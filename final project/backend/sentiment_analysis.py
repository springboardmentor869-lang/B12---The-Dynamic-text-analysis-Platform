import re
from transformers import pipeline

# =====================================================
# LOAD MODEL ONCE
# =====================================================

import torch

# Determine device (GPU if available, else CPU)
device = 0 if torch.cuda.is_available() else -1

classifier = pipeline(
    "sentiment-analysis",
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    device=device
)

# Model labels for lxyuan/distilbert-base-multilingual-cased-sentiments-student
# Usually returns: 'positive', 'neutral', 'negative'
LABEL_MAP = {
    "positive": "positive",
    "neutral": "neutral",
    "negative": "negative"
}

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

    # Process ALL sentences
    # Truncate each sentence to 512 chars to prevent model input errors
    processed_sentences = [s[:512] for s in sentences]

    # ── BATCH inference: process everything in batches for efficiency ──
    try:
        results = classifier(processed_sentences, batch_size=64, truncation=True)
    except Exception as e:
        print("Batch sentiment error:", e)
        results = [{"label": "neutral", "score": 0.0}] * len(processed_sentences)

    positive = 0
    negative = 0
    neutral = 0
    total_confidence = 0
    sentence_level = []

    for sentence, result in zip(sentences, results):
        # Map label to positive/negative/neutral
        raw_label = result["label"].lower()
        label = LABEL_MAP.get(raw_label, raw_label)
        
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
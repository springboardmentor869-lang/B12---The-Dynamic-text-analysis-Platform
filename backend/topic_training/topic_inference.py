import re

# -------------------------------------------------------
# Keyword-based Topic Classifier
# -------------------------------------------------------

TOPIC_KEYWORDS = {
    "artificial intelligence": [
        "artificial intelligence", "ai", "machine learning",
        "deep learning", "neural network", "automation", "model"
    ],
    "healthcare": [
        "hospital", "doctor", "patient", "medical", "diagnosis",
        "healthcare", "disease", "treatment", "medicine"
    ],
    "education": [
        "education", "student", "teacher", "learning",
        "school", "academic", "classroom", "institution"
    ],
    "technology": [
        "technology", "digital", "software", "system",
        "application", "tool", "platform", "innovation"
    ],
    "business": [
        "business", "market", "industry", "growth",
        "organization", "company", "management"
    ]
}


# -------------------------------------------------------
# TEXT PREPROCESSING
# -------------------------------------------------------

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_chunks(text, chunk_size=500):
    return [
        text[i:i+chunk_size].strip()
        for i in range(0, len(text), chunk_size)
        if text[i:i+chunk_size].strip()
    ]


# -------------------------------------------------------
# CHUNK-LEVEL TOPIC CLASSIFICATION
# -------------------------------------------------------

def classify_chunk(chunk):
    cleaned_chunk = preprocess_text(chunk)
    topic_scores = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            score += cleaned_chunk.count(keyword.lower())
        topic_scores[topic] = score

    filtered_topics = {k: v for k, v in topic_scores.items() if v > 0}

    if not filtered_topics:
        return "General", 0

    best_topic = max(filtered_topics, key=filtered_topics.get)
    best_score = filtered_topics[best_topic]

    return best_topic, best_score


# -------------------------------------------------------
# MAIN DOCUMENT CLASSIFICATION
# -------------------------------------------------------

def classify_document(text):
    cleaned_text = preprocess_text(text)

    topic_scores = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            score += cleaned_text.count(keyword.lower())
        topic_scores[topic] = score

    filtered_topics = {k: v for k, v in topic_scores.items() if v > 0}

    if not filtered_topics:
        return {
            "dominant_topic": "General",
            "avg_score": 0.0,
            "topics": [],
            "chunk_results": [],
            "report": "No dominant topic could be strongly identified from the document."
        }

    sorted_topics = sorted(filtered_topics.items(), key=lambda x: x[1], reverse=True)

    total_score = sum(filtered_topics.values())
    topic_list = []

    for idx, (topic, score) in enumerate(sorted_topics):
        normalized_score = round(score / total_score, 4) if total_score > 0 else 0.0

        topic_list.append({
            "topic_id": idx,
            "topic": topic,
            "chunks_matched": score,
            "avg_score": normalized_score,
            "score": normalized_score
        })

    dominant_topic = sorted_topics[0][0]
    avg_score = round(topic_list[0]["avg_score"], 4) if topic_list else 0.0

    chunks = split_into_chunks(text, chunk_size=500)
    chunk_results = []

    for idx, chunk in enumerate(chunks):
        topic, score = classify_chunk(chunk)
        chunk_results.append({
            "chunk_id": idx + 1,
            "text": chunk,
            "topic": topic,
            "score": score
        })

    report = f"""
Topic Modeling Report:
The dominant topic identified in the uploaded document is "{dominant_topic}".

A total of {len(topic_list)} major topics were detected based on keyword distribution.
The average confidence score for the dominant topic is {avg_score}.

Chunk-level topic analysis was also performed to understand how themes are distributed throughout the document.
""".strip()

    return {
        "dominant_topic": dominant_topic,
        "avg_score": avg_score,
        "topics": topic_list,
        "chunk_results": chunk_results,
        "report": report
    }
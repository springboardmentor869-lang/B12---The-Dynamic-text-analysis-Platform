import json
import numpy as np
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# LOAD MODEL
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
model = BERTopic.load("models/bertopic_model", embedding_model=embedding_model)

with open("models/topic_centroids.json") as f:
    centroids = json.load(f)

# =========================
# SMART LABEL FUNCTION
# =========================
def smart_label(text):
    t = text.lower()

    if any(w in t for w in ["health", "hospital", "doctor", "medicine"]):
        return "Healthcare Systems"

    if any(w in t for w in ["finance", "stock", "bank", "money"]):
        return "Financial Markets"

    if any(w in t for w in ["climate", "environment", "global warming"]):
        return "Climate Change"

    if any(w in t for w in ["education", "school", "student"]):
        return "Education Systems"

    if any(w in t for w in ["ai", "machine", "technology", "robot"]):
        return "Artificial Intelligence"

    return "General Knowledge"

# =========================
# MODEL PREDICTION
# =========================
def predict_model(text):
    topic, _ = model.transform([text])
    return smart_label(text)

# =========================
# FAST PREDICTION
# =========================
def predict_fast(text):
    emb = embedding_model.encode([text])[0]

    best = None
    best_score = -1

    for tid, centroid in centroids.items():
        score = cosine_similarity([emb], [centroid])[0][0]
        if score > best_score:
            best_score = score
            best = tid

    return smart_label(text)

# =========================
# LOOP
# =========================
while True:
    text = input("Enter text: ")

    if text.lower() == "exit":
        break

    print("\nModel Prediction:", predict_model(text))
    print("Fast Prediction:", predict_fast(text))
    print("-" * 40)
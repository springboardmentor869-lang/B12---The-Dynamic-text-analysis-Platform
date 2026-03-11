import os
import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

from doc_parser import load_pdf, split_into_chunks


MODEL_DIR = "models"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


# ---------------------------------------
# Load trained artifacts
# ---------------------------------------
def load_artifacts():

    with open(os.path.join(MODEL_DIR, "centroids.pkl"), "rb") as f:
        centroids = pickle.load(f)

    with open(os.path.join(MODEL_DIR, "topic_labels.json"), "r") as f:
        topic_labels = json.load(f)

    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print(f"Loaded {len(centroids)} topic centroids")

    return centroids, topic_labels, embedding_model


# ---------------------------------------
# Cosine Similarity
# ---------------------------------------
def cosine_similarity(vec1, vec2):

    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0

    return float(np.dot(vec1, vec2) / (norm1 * norm2))


# ---------------------------------------
# Classify a single chunk
# ---------------------------------------
def classify_chunk(chunk_embedding, centroids, topic_labels):

    best_topic = None
    best_score = -1

    for topic_id, centroid in centroids.items():

        score = cosine_similarity(chunk_embedding, centroid["centroid"])

        if score > best_score:
            best_score = score
            best_topic = topic_id

    return {
        "topic_id": best_topic,
        "label": topic_labels[str(best_topic)],
        "score": round(best_score, 4)
    }


# ---------------------------------------
# Classify full document
# ---------------------------------------
def classify_document(file_path, chunk_size=500):

    centroids, topic_labels, embedding_model = load_artifacts()

    print(f"\nLoading document: {file_path}")

    raw_text = load_pdf(file_path)

    chunks = split_into_chunks(raw_text, chunk_size)

    print(f"Split into {len(chunks)} chunks")

    print("Embedding chunks...")

    embeddings = embedding_model.encode(chunks)

    results = []

    for emb in embeddings:
        result = classify_chunk(emb, centroids, topic_labels)
        results.append(result)

    return results


# ---------------------------------------
# Main
# ---------------------------------------
if __name__ == "__main__":

    results = classify_document("documents/sample.pdf")

    print("\n==============================")
    print("DOCUMENT CLASSIFICATION RESULT")
    print("==============================\n")

    for i, r in enumerate(results):
        print(f"Chunk {i+1} → {r}")
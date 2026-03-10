import os
import pickle
import json
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_DIR = "models"
INPUT_FILE = "input_docs/converted.md"
OUTPUT_FILE = "outputs/result.json"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 100


def load_models():

    with open(os.path.join(MODEL_DIR, "topic_centroids.pkl"), "rb") as f:
        centroids = pickle.load(f)

    with open(os.path.join(MODEL_DIR, "topic_labels.json"), "r") as f:
        labels = json.load(f)

    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f"Loaded {len(centroids)} topic centroids")

    return centroids, labels, model


def load_markdown(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def split_chunks(text, chunk_size=500):

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def cosine_similarity(a, b):

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def classify_chunk(embedding, centroids):

    best_score = -1
    best_topic = None
    best_label = None

    for tid, data in centroids.items():

        score = cosine_similarity(embedding, data["centroid"])

        if score > best_score:
            best_score = score
            best_topic = tid
            best_label = data["label"]

    return {
        "topic_id": best_topic,
        "label": best_label,
        "score": round(best_score, 4)
    }


def classify_document():

    centroids, labels, model = load_models()

    print("\nLoading document...")
    text = load_markdown(INPUT_FILE)

    chunks = split_chunks(text, CHUNK_SIZE)

    print(f"Split into {len(chunks)} chunks")

    embeddings = model.encode(chunks)

    results = []

    for chunk, emb in zip(chunks, embeddings):

        result = classify_chunk(emb, centroids)
        result["preview"] = chunk[:100]

        results.append(result)

    return results


def save_results(results):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == "__main__":

    results = classify_document()

    print("\nDYNAMIC TEXT CLASSIFICATION REPORT\n")

    for i, r in enumerate(results, 1):

        print(f"Chunk {i}")
        print(f"Topic: {r['label']}")
        print(f"Score: {r['score']}")
        print(f"Preview: {r['preview']}\n")

    save_results(results)
    
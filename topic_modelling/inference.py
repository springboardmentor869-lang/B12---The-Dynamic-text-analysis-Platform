import os
import pickle
import json
import numpy as np

from sentence_transformers import SentenceTransformer

# ================================
# CONFIG
# ================================

MODEL_DIR = os.getenv("MODEL_DIR", "models")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
SIMILARITY_THRESHOLD = 0.20


# ================================
# LOAD ARTIFACTS
# ================================

def load_artifacts():

    with open(os.path.join(MODEL_DIR, "topic_centroids.pkl"), "rb") as f:
        centroids = pickle.load(f)

    with open(os.path.join(MODEL_DIR, "topic_labels.json"), "r") as f:
        topic_labels = json.load(f)

    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print(f"Loaded {len(centroids)} topic centroids.")

    return centroids, topic_labels, embedding_model


# ================================
# LOAD MARKDOWN FILE
# ================================

def load_markdown(file_path: str) -> str:

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# ================================
# SPLIT INTO CHUNKS
# ================================

def split_into_chunks(text: str, chunk_size: int = 500) -> list:

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks


# ================================
# COSINE SIMILARITY
# ================================

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:

    return np.dot(vec1, vec2) / (
        np.linalg.norm(vec1) * np.linalg.norm(vec2)
    )


# ================================
# CLASSIFY CHUNK
# ================================

def classify_chunk(chunk_embedding, centroids):

    best_topic_id = None
    best_score = -1
    best_label = "Out of Domain"
    best_keywords = []

    for topic_id, data in centroids.items():

        score = cosine_similarity(chunk_embedding, data["centroid"])

        if score > best_score:
            best_score = score
            best_topic_id = topic_id
            best_label = data["label"]
            best_keywords = data.get("keywords", [])

    if best_score < SIMILARITY_THRESHOLD:
        return {
            "topic_id": -1,
            "label": "Out of Domain",
            "score": round(best_score, 4),
            "keywords": []
        }

    return {
        "topic_id": best_topic_id,
        "label": best_label,
        "score": round(best_score, 4),
        "keywords": best_keywords
    }


# ================================
# CLASSIFY DOCUMENT
# ================================

def classify_document(file_path: str, chunk_size: int = 500):

    centroids, topic_labels, embedding_model = load_artifacts()

    print(f"\nLoading document: {file_path}")
    raw_text = load_markdown(file_path)

    print(f"Document length: {len(raw_text.split())} words")

    chunks = split_into_chunks(raw_text, chunk_size)

    print(f"Split into {len(chunks)} chunks ({chunk_size} words each)")
    print("Embedding chunks...")

    embeddings = embedding_model.encode(chunks, show_progress_bar=True)

    chunk_results = []
    topic_counts = {}

    for idx, embedding in enumerate(embeddings):

        result = classify_chunk(embedding, centroids)

        # Add preview text
        result["preview"] = chunks[idx][:120].replace("\n", " ")

        chunk_results.append(result)

        tid = result["topic_id"]

        if tid not in topic_counts:
            topic_counts[tid] = {
                "label": result["label"],
                "count": 0,
                "scores": []
            }

        topic_counts[tid]["count"] += 1
        topic_counts[tid]["scores"].append(result["score"])

    dominant_topic_id = max(topic_counts, key=lambda x: topic_counts[x]["count"])

    dominant_label = topic_counts[dominant_topic_id]["label"]
    avg_score = np.mean(topic_counts[dominant_topic_id]["scores"])

    return {
        "file": file_path,
        "dominant_topic": {
            "topic_id": dominant_topic_id,
            "label": dominant_label,
            "avg_similarity_score": round(avg_score, 4),
            "chunks_matched": topic_counts[dominant_topic_id]["count"],
            "total_chunks": len(chunks)
        },
        "all_topics_found": [
            {
                "topic_id": tid,
                "label": data["label"],
                "chunks_matched": data["count"],
                "avg_score": round(np.mean(data["scores"]), 4)
            }
            for tid, data in sorted(
                topic_counts.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )
        ],
        "chunk_details": chunk_results
    }


# ================================
# MAIN
# ================================

if __name__ == "__main__":

    file_path = "md_outputs/converted.md"

    result = classify_document(file_path, chunk_size=500)

    dt = result["dominant_topic"]

    print("\n")
    print("╔" + "═" * 70 + "╗")
    print("║" + " DYNAMIC TEXT CLASSIFICATION REPORT ".center(70) + "║")
    print("╚" + "═" * 70 + "╝")

    print(f"\n File: {result['file']}")
    print(f" Dominant Topic: [{dt['topic_id']}] {dt['label']}")
    print(f" Avg Similarity: {dt['avg_similarity_score']}")
    print(f" Chunks Matched: {dt['chunks_matched']} / {dt['total_chunks']}")

    print("\n" + "─" * 72)
    print(" TOPIC DISTRIBUTION ")
    print("─" * 72)

    for topic in result["all_topics_found"]:
        bar = "█" * topic["chunks_matched"]
        print(
            f"[{str(topic['topic_id']).rjust(2)}] "
            f"{topic['label']:<30} "
            f"{bar:<10} "
            f"{topic['chunks_matched']} chunks "
            f"(avg: {topic['avg_score']})"
        )

    print("\n" + "─" * 72)
    print(" CHUNK BREAKDOWN ")
    print("─" * 72)

    for i, chunk in enumerate(result["chunk_details"], start=1):

        print(f"\n#{str(i).rjust(2)}  →  [{chunk['topic_id']}] {chunk['label']}")
        print(f"     Score: {chunk['score']}")
        print(f"     Preview: {chunk['preview'][:100]}...")
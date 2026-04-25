import os
import pickle
import json
import numpy as np
from sentence_transformers import SentenceTransformer


# =====================================================
# CONFIG
# =====================================================

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.20


# =====================================================
# LOAD MODEL ARTIFACTS
# =====================================================

def load_artifacts():

    with open(os.path.join(MODEL_DIR, "topic_centroids.pkl"), "rb") as f:
        centroids = pickle.load(f)

    with open(os.path.join(MODEL_DIR, "topic_labels.json"), "r") as f:
        topic_labels = json.load(f)

    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print(f"\nLoaded {len(centroids)} topic centroids.")

    return centroids, topic_labels, embedding_model


# =====================================================
# LOAD MARKDOWN
# =====================================================

def load_markdown(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# =====================================================
# SPLIT TEXT
# =====================================================

def split_into_chunks(text, chunk_size=500):

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks


# =====================================================
# COSINE SIMILARITY
# =====================================================

def cosine_similarity(v1, v2):

    return np.dot(v1, v2) / (
        np.linalg.norm(v1) * np.linalg.norm(v2)
    )


# =====================================================
# CLASSIFY SINGLE CHUNK
# =====================================================

def classify_chunk(chunk_embedding, centroids):

    best_topic = None
    best_score = -1
    best_label = "Out of Domain"

    for topic_id, data in centroids.items():

        score = cosine_similarity(chunk_embedding, data["centroid"])

        if score > best_score:

            best_score = score
            best_topic = topic_id
            best_label = data["label"]

    if best_score < SIMILARITY_THRESHOLD:

        return {
            "topic_id": -1,
            "label": "Out of Domain",
            "score": round(float(best_score), 4)
        }

    return {
        "topic_id": best_topic,
        "label": best_label,
        "score": round(float(best_score), 4)
    }


# =====================================================
# DOCUMENT CLASSIFICATION
# =====================================================

def classify_document(file_path, chunk_size=500):

    centroids, topic_labels, embedding_model = load_artifacts()

    print(f"\nLoading document: {file_path}")

    text = load_markdown(file_path)

    word_count = len(text.split())

    print(f"Document length: {word_count} words")

    chunks = split_into_chunks(text, chunk_size)

    print(f"Split into {len(chunks)} chunks ({chunk_size} words each)")

    print("\nEmbedding chunks...")

    embeddings = embedding_model.encode(chunks, show_progress_bar=True)

    print("\nClassifying chunks...\n")

    topic_counts = {}
    chunk_results = []

    for i, emb in enumerate(embeddings):

        result = classify_chunk(emb, centroids)

        preview = chunks[i][:100].replace("\n", " ")

        result["preview"] = preview

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

    dominant_topic = max(topic_counts, key=lambda x: topic_counts[x]["count"])

    dominant_label = topic_counts[dominant_topic]["label"]

    avg_score = round(float(np.mean(topic_counts[dominant_topic]["scores"])), 4)

    result = {

        "file": file_path,

        "dominant_topic": {
            "topic_id": dominant_topic,
            "label": dominant_label,
            "avg_similarity_score": avg_score,
            "chunks_matched": topic_counts[dominant_topic]["count"],
            "total_chunks": len(chunks)
        },

        "all_topics_found": [

            {
                "topic_id": tid,
                "label": data["label"],
                "chunks_matched": data["count"],
                "avg_score": round(float(np.mean(data["scores"])), 4)
            }

            for tid, data in sorted(
                topic_counts.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )
        ],

        "chunk_details": chunk_results
    }

    return result


# =====================================================
# SAVE JSON
# =====================================================

def save_result_json(result):

    os.makedirs("outputs", exist_ok=True)

    with open("outputs/result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    print("\nResults saved to outputs/result.json")


if __name__ == "__main__":

    file_path = os.path.join(BASE_DIR, "markdown_outputs", "sample.md")

    result = classify_document(file_path)

    dt = result["dominant_topic"]

    print("\n" + "="*60)
    print("DYNAMIC TEXT CLASSIFICATION REPORT")
    print("="*60)

    print(f"\nFile: {result['file']}")
    print(f"Dominant Topic: [{dt['topic_id']}] {dt['label']}")
    print(f"Avg Similarity Score: {dt['avg_similarity_score']}")
    print(f"Chunks Matched: {dt['chunks_matched']} / {dt['total_chunks']}")

    print("\nTopic Distribution:\n")

    for topic in result["all_topics_found"]:
        print(
            f"[{topic['topic_id']}] {topic['label']} "
            f"→ {topic['chunks_matched']} chunks "
            f"(avg score: {topic['avg_score']})"
        )

    print("\nChunk Analysis:\n")

    for i, chunk in enumerate(result["chunk_details"], start=1):
        print(f"Chunk {i}")
        print(f"Topic : {chunk['label']}")
        print(f"Score : {chunk['score']}")
        print(f"Preview : {chunk['preview']}\n")

    save_result_json(result)
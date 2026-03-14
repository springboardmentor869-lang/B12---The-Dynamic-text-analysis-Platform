import os
import json
import pickle
import numpy as np
import requests
import pandas as pd
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN

load_dotenv()

# -----------------------------
# 1️⃣ LLM LABEL GENERATION
# -----------------------------
def generate_topic_label_with_ollama(keywords, docs, model="llama3"):
    prompt = f"""
    Generate a concise human-readable label (2-5 words) for a topic.
    Keywords: {', '.join(keywords)}
    Sample text: {' '.join(docs[:2])[:500]}
    Respond with ONLY the label.
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()
        label = response.json().get("response", "").strip()
        return label if label else "Unknown Topic"

    except Exception as e:
        print("LLM Error:", e)
        return "Unknown Topic"


# -----------------------------
# 2️⃣ MAIN TRAINING FUNCTION
# -----------------------------
def main():

    print("📥 Loading custom dataset...")

    df = pd.read_csv("custom_tech_dataset.csv")

    if "text" not in df.columns:
        raise ValueError("CSV must contain a column named 'text'")

    docs = df["text"].dropna().tolist()
    print(f"Loaded {len(docs)} documents")

    # -----------------------------
    # 3️⃣ Configure Models
    # -----------------------------
    print("⚙ Configuring embedding, UMAP, HDBSCAN...")

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    umap_model = UMAP(
        n_neighbors=10,
        n_components=5,
        min_dist=0.0,
        metric="cosine",
        random_state=42
    )

    hdbscan_model = HDBSCAN(
        min_cluster_size=5,      # smaller → more clusters
        min_samples=3,
        metric="euclidean",
        cluster_selection_method="eom",
        prediction_data=True
    )

    # ❗ No nr_topics here
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        verbose=True
    )

    # -----------------------------
    # 4️⃣ Train Model
    # -----------------------------
    print("🚀 Training BERTopic model...")
    topics, probs = topic_model.fit_transform(docs)

    initial_topics = len(set(topics)) - (1 if -1 in topics else 0)
    print("Initial topics found:", initial_topics)

    # -----------------------------
    # 5️⃣ Reduce to 40 Topics (SAFE WAY)
    # -----------------------------
    print("🔽 Reducing to 40 topics...")
    topic_model = topic_model.reduce_topics(docs, nr_topics=40)

    final_topics = len(topic_model.get_topics()) - 1
    print("Final topic count:", final_topics)

    # -----------------------------
    # 6️⃣ Generate Topic Labels + Centroids
    # -----------------------------
    print("🧠 Generating topic labels using LLM...")

    topic_info = topic_model.get_topic_info()
    rep_docs = topic_model.representative_docs_

    topic_labels = {}
    centroids = {}

    for _, row in topic_info.iterrows():
        topic_id = row["Topic"]

        if topic_id == -1:
            continue

        print(f"Processing topic {topic_id}...")

        topic_words = topic_model.get_topic(topic_id)
        keywords = [word for word, _ in topic_words[:10]] if topic_words else []

        docs_list = rep_docs.get(topic_id, [])

        label = generate_topic_label_with_ollama(keywords, docs_list)
        topic_labels[topic_id] = label

        if docs_list:
            embeddings = embedding_model.encode(docs_list)
            centroid = np.mean(embeddings, axis=0)

            centroids[topic_id] = {
                "label": label,
                "centroid": centroid.tolist(),
                "keywords": keywords
            }

    # -----------------------------
    # 7️⃣ Save Artifacts
    # -----------------------------
    print("💾 Saving model artifacts...")

    output_dir = "models"
    os.makedirs(output_dir, exist_ok=True)

    topic_model.save(os.path.join(output_dir, "bertopic_model"))

    with open(os.path.join(output_dir, "centroids.pkl"), "wb") as f:
        pickle.dump(centroids, f)

    with open(os.path.join(output_dir, "topic_labels.json"), "w") as f:
        json.dump(topic_labels, f, indent=2)

    print("🎉 Training complete!")
    print(f"📂 Saved inside: {output_dir}/")


if __name__ == "__main__":
    main()
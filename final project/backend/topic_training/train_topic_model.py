import os
import json
import pickle
import numpy as np

from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from umap import UMAP
import hdbscan

# ================================
# CONFIG
# ================================

BASE_DIR = os.path.dirname(__file__)

DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "documents.txt")

MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

os.makedirs(MODEL_DIR, exist_ok=True)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ================================
# LOAD DATASET
# ================================

def load_dataset():

    docs = []

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            text = line.strip()

            if len(text) > 20:
                docs.append(text)

    print("Documents loaded:", len(docs))

    return docs


# ================================
# TRAIN TOPIC MODEL
# ================================

def train_topic_model():

    docs = load_dataset()

    print("Loading embedding model...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("Generating embeddings...")
    embeddings = embedding_model.encode(docs, show_progress_bar=True)

    print("Configuring UMAP...")
    umap_model = UMAP(
        n_neighbors=15,
        n_components=5,
        min_dist=0.0,
        metric="cosine"
    )

    print("Configuring HDBSCAN...")
    hdbscan_model = hdbscan.HDBSCAN(
        min_cluster_size=15,
        metric="euclidean",
        cluster_selection_method="eom"
    )

    print("Training BERTopic model...")

    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        verbose=True
    )

    topics, probs = topic_model.fit_transform(docs, embeddings)

    print("Reducing topics to 40...")
    topic_model.reduce_topics(docs, nr_topics=40)

    topic_info = topic_model.get_topic_info()

    topic_labels = {}

    for _, row in topic_info.iterrows():

        topic_id = int(row["Topic"])

        if topic_id == -1:
            continue

        words = topic_model.get_topic(topic_id)

        label = " ".join([w[0] for w in words[:3]])

        topic_labels[topic_id] = label

    print("Computing topic centroids...")

    topic_centroids = {}

    for topic_id in topic_labels:

        indices = [i for i, t in enumerate(topics) if t == topic_id]

        if len(indices) == 0:
            continue

        topic_embeddings = embeddings[indices]

        centroid = np.mean(topic_embeddings, axis=0)

        topic_centroids[topic_id] = {
            "centroid": centroid,
            "label": topic_labels[topic_id]
        }

    print("Saving model artifacts...")

    topic_model.save(os.path.join(MODEL_DIR, "bertopic_model"))

    with open(os.path.join(MODEL_DIR, "topic_centroids.pkl"), "wb") as f:
        pickle.dump(topic_centroids, f)

    with open(os.path.join(MODEL_DIR, "topic_labels.json"), "w") as f:
        json.dump(topic_labels, f, indent=4)

    print("\nTraining completed successfully!")
    print("Saved to:", MODEL_DIR)


# ================================
# MAIN
# ================================

if __name__ == "__main__":

    train_topic_model()
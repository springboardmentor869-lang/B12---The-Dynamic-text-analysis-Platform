import os
import json
import pickle
import numpy as np
import pandas as pd
import torch

from sentence_transformers import SentenceTransformer
from umap import UMAP
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize


# =============================
# CONFIG
# =============================
DATA_PATH = "data/dataset.csv"
MODEL_DIR = "models"
NUM_TOPICS = 40


# =============================
# LOAD DATASET
# =============================
print("Loading dataset...")

df = pd.read_csv(DATA_PATH)
documents = df["text"].dropna().tolist()
print(f"Loaded {len(documents)} documents")


# =============================
# LOAD EMBEDDING MODEL
# =============================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device=device
)


# =============================
# CREATE EMBEDDINGS
# =============================
print("Generating embeddings...")
embeddings = embedding_model.encode(
    documents,
    batch_size=16,
    show_progress_bar=True
)


# =============================
# REDUCE DIMENSIONS (UMAP)
# =============================
print("Applying UMAP...")
umap_model = UMAP(
    n_neighbors=15,
    n_components=5,
    min_dist=0.0,
    metric="cosine"
)

reduced_embeddings = umap_model.fit_transform(embeddings)


# =============================
# CLUSTER USING KMEANS
# =============================
print(f"Clustering into {NUM_TOPICS} topics...")
kmeans = KMeans(n_clusters=NUM_TOPICS, random_state=42)
topics = kmeans.fit_predict(reduced_embeddings)


# =============================
# GENERATE LABELS + CENTROIDS
# =============================
print("Generating topic labels and computing centroids...")

topic_labels = {}
centroids = {}

for topic_id in range(NUM_TOPICS):

    print(f"\nLabeling topic {topic_id}...")

    topic_docs = [
        documents[i]
        for i in range(len(documents))
        if topics[i] == topic_id
    ]

    if not topic_docs:
        print(f"Topic {topic_id} has no documents. Skipping.")
        continue

    # Create label from first document
    first_doc = topic_docs[0]
    words = first_doc.split()[:3]
    label = " ".join(words).title()

    print(f"Topic {topic_id}: \"{label}\"")

    topic_labels[topic_id] = label

    # Compute centroid
    topic_embeddings = [
        embeddings[i]
        for i in range(len(embeddings))
        if topics[i] == topic_id
    ]

    centroid = np.mean(topic_embeddings, axis=0)
    centroid = normalize([centroid])[0]

    centroids[topic_id] = {
        "label": label,
        "centroid": centroid.tolist()
    }


# =============================
# SAVE ARTIFACTS
# =============================
print("\nSaving topic labels...")
print("Saving centroids...")

os.makedirs(MODEL_DIR, exist_ok=True)

with open(os.path.join(MODEL_DIR, "topic_labels.json"), "w") as f:
    json.dump(topic_labels, f, indent=4)

with open(os.path.join(MODEL_DIR, "topic_centroids.pkl"), "wb") as f:
    pickle.dump(centroids, f)

print("\nPipeline complete.")
print("Task 7 completed successfully.")

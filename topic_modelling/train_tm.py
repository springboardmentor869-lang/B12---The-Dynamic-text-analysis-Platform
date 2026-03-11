import os
import pickle
import numpy as np
import pandas as pd
import requests
import torch

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.preprocessing import normalize


# =============================
# CONFIG
# =============================
DATA_PATH = "custom_dataset.csv"
MODEL_DIR = "models"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"   # Best for 4GB VRAM


# =============================
# LOAD DATASET
# =============================
print("Loading dataset...")

try:
    df = pd.read_csv(DATA_PATH)
    documents = df["text"].dropna().tolist()
    print(f"Loaded {len(documents)} documents")
except Exception as e:
    print(f"Dataset loading error: {e}")
    exit()


# =============================
# LOAD EMBEDDING MODEL
# =============================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

try:
    embedding_model = SentenceTransformer(
        "all-MiniLM-L6-v2",
        device=device
    )
except Exception as e:
    print(f"Embedding model error: {e}")
    exit()


# =============================
# CONFIGURE UMAP + HDBSCAN
# =============================
umap_model = UMAP(
    n_neighbors=15,
    n_components=5,
    min_dist=0.0,
    metric="cosine"
)

hdbscan_model = HDBSCAN(
    min_cluster_size=6,
    min_samples=3,
    metric='euclidean',
    cluster_selection_method='eom',
    prediction_data=True
)


# =============================
# INITIALIZE BERTopic
# =============================
topic_model = BERTopic(
    embedding_model=embedding_model,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    verbose=True
)


# =============================
# TRAIN MODEL
# =============================
print("Training BERTopic model...")

try:
    topics, probs = topic_model.fit_transform(documents)

    initial_topic_count = len(topic_model.get_topics())
    print(f"Initial discovered topics: {initial_topic_count}")

    if initial_topic_count > 40:
        topic_model.reduce_topics(documents, nr_topics=40)
        print("Reduced to 40 topics")
    else:
        print("Topic count is already <= 40. No reduction applied.")

except Exception as e:
    print(f"Training error: {e}")
    exit()


# =============================
# SAVE MODEL
# =============================
os.makedirs(MODEL_DIR, exist_ok=True)

try:
    topic_model.save(os.path.join(MODEL_DIR, "bertopic_model"))
except Exception as e:
    print(f"Model saving error: {e}")


# =============================
# GET REPRESENTATIVE DOCS
# =============================
print("Extracting representative documents...")

topic_info = topic_model.get_document_info(documents)
rep_docs_per_topic = {}

for topic_id in topic_info["Topic"].unique():
    if topic_id == -1:
        continue

    docs = topic_info[
        topic_info["Topic"] == topic_id
    ]["Document"].head(5).tolist()

    rep_docs_per_topic[topic_id] = docs


# =============================
# OLLAMA LABEL GENERATION
# =============================
def generate_topic_label_with_ollama(keywords, docs):

    prompt = f"""
Generate a concise 2-4 word topic label.

Keywords: {', '.join(keywords)}

Example text:
{docs[0][:500] if docs else ""}

Respond with ONLY the label.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()
        label = response.json().get("response", "").strip()
        return label if label else "Unknown Topic"

    except Exception as e:
        print(f"Ollama error: {e}")
        return "Unknown Topic"


print("Generating topic labels...")

topic_labels = {}
centroids = {}

for topic_id, docs in rep_docs_per_topic.items():

    try:
        topic_words = topic_model.get_topic(topic_id)
        keywords = [word for word, _ in topic_words[:10]] if topic_words else []
    except Exception as e:
        print(f"Keyword extraction error for topic {topic_id}: {e}")
        keywords = []

    print(f"Labeling topic {topic_id}...")

    label = generate_topic_label_with_ollama(keywords, docs)
    topic_labels[topic_id] = label

    # Compute centroid safely
    try:
        if docs:
            embeddings = embedding_model.encode(
                docs,
                batch_size=8,  # Safe for 4GB VRAM
                show_progress_bar=False
            )
            centroid = np.mean(embeddings, axis=0)
            centroid = normalize([centroid])[0]

            centroids[topic_id] = {
                "label": label,
                "centroid": centroid
            }

    except Exception as e:
        print(f"Centroid computation error for topic {topic_id}: {e}")

# =============================
# EXPORT SIMPLE LABEL JSON
# =============================
import json

print("Exporting simple labels JSON...")

simple_labels = []

for topic_id, label in topic_labels.items():
    simple_labels.append({
        "id": int(topic_id),
        "label": label
    })

with open(os.path.join(MODEL_DIR, "topic_labels.json"), "w", encoding="utf-8") as f:
    json.dump(simple_labels, f, indent=4)

print("topic_labels.json saved successfully.")
# =============================
# SAVE ARTIFACTS
# =============================
try:
    with open(os.path.join(MODEL_DIR, "topic_centroids.pkl"), "wb") as f:
        pickle.dump(centroids, f)

    with open(os.path.join(MODEL_DIR, "topic_labels.pkl"), "wb") as f:
        pickle.dump(topic_labels, f)

    print("All artifacts saved successfully.")

except Exception as e: 
    print(f"Saving error: {e}")


print("Pipeline complete.")
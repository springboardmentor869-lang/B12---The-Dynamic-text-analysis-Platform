import os
import json
import numpy as np
import umap
import hdbscan

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer


#  Load Dataset

print("Loading documents...")

with open("data/documents.txt", "r", encoding="utf-8") as f:
    documents = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(documents)} documents")


# Configure BERTopic

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

umap_model = umap.UMAP(
    n_neighbors=10,
    n_components=5,
    min_dist=0.0,
    metric="cosine",
    random_state=42
)

hdbscan_model = hdbscan.HDBSCAN(
    min_cluster_size=5,
    min_samples=2,
    metric="euclidean",
    cluster_selection_method="eom",
    prediction_data=True
)

vectorizer_model = CountVectorizer(stop_words="english")

topic_model = BERTopic(
    embedding_model=embedding_model,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    vectorizer_model=vectorizer_model,
    calculate_probabilities=True,
    verbose=True
)


#  Train Model

print("Training model...")
topics, probs = topic_model.fit_transform(documents)

print("Reducing to 40 topics...")
topic_model = topic_model.reduce_topics(documents, nr_topics=40)


# Generate Labels

print("Generating topic labels...")

topic_info = topic_model.get_topic_info()
topic_labels = {}

for topic_id in topic_info.Topic:
    if topic_id == -1:
        continue

    words = topic_model.get_topic(topic_id)
    keywords = [word for word, _ in words[:5]]

    label = "Topic about " + ", ".join(keywords)
    topic_labels[int(topic_id)] = label


#  Compute Centroids

print("Computing centroids...")

embeddings = embedding_model.encode(documents)

topic_centroids = {}

for topic_id in set(topics):
    if topic_id == -1:
        continue

    topic_docs_idx = [i for i, t in enumerate(topics) if t == topic_id]
    topic_embeddings = embeddings[topic_docs_idx]

    centroid = np.mean(topic_embeddings, axis=0)
    topic_centroids[int(topic_id)] = centroid.tolist()


# Save Everything

os.makedirs("models", exist_ok=True)

topic_model.save("models/bertopic_model")

with open("models/topic_labels.json", "w") as f:
    json.dump(topic_labels, f, indent=2)

with open("models/topic_centroids.json", "w") as f:
    json.dump(topic_centroids, f, indent=2)

print("\n✅ Training Complete!")
print("Artifacts saved in 'models/' folder")
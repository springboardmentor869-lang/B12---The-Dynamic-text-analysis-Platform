import os
import pickle
import json

from sklearn.datasets import fetch_20newsgroups
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic


MODEL_DIR = "models"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def main():

    os.makedirs(MODEL_DIR, exist_ok=True)

    print("Loading dataset...")

    dataset = fetch_20newsgroups(
        subset="all",
        remove=("headers", "footers", "quotes")
    )

    docs = dataset.data

    print("Loading embedding model...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("Training BERTopic model...")

    topic_model = BERTopic(
        embedding_model=embedding_model,
        verbose=True
    )

    topics, probs = topic_model.fit_transform(docs)

    print("Saving BERTopic model...")

    topic_model.save(os.path.join(MODEL_DIR, "bertopic_model"))

    print("Extracting topic centroids...")

    topic_embeddings = topic_model.topic_embeddings_

    centroids = {}

    for topic_id, embedding in enumerate(topic_embeddings):
        centroids[topic_id] = {
            "centroid": embedding.tolist(),
            "label": f"Topic {topic_id}",
            "keywords": []
        }

    with open(os.path.join(MODEL_DIR, "centroids.pkl"), "wb") as f:
        pickle.dump(centroids, f)

    labels = {str(k): v["label"] for k, v in centroids.items()}

    with open(os.path.join(MODEL_DIR, "topic_labels.json"), "w") as f:
        json.dump(labels, f, indent=4)

    print("Training complete.")


if __name__ == "__main__":
    main()
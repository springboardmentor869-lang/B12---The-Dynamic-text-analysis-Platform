import os
import pickle
import json
from pathlib import Path
import numpy as np
import requests
from sklearn.datasets import fetch_20newsgroups
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import dotenv

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parents[1]
dotenv.load_dotenv(ROOT_DIR / ".env")

# Output directory for trained model artifacts
MODEL_DIR = ROOT_DIR / "models" / "bertopic_20newsgroups"

def generate_topic_label_with_ollama(keywords: list, docs: list, model: str = "kimi-k2.5:cloud") -> str:
    """
    Generates a single topic label using Ollama local model.
    - No rate limits since it runs locally.
    - model: any model pulled in Ollama (e.g., llama3, mistral, qwen2.5:3b)
    """
    prompt = (
        f"Generate a concise, human-readable label (2-5 words) for a topic "
        f"based on these keywords: {', '.join(keywords)}. "
        f"Sample text: {' '.join(docs[:2])[:500]}. " 
        f"Respond with ONLY the label, nothing else."
    )
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json={
                "model": model,
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

def main():
    print("Fetching 20 Newsgroups dataset...")
    newsgroups = fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'))
    docs = newsgroups.data

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    topic_model = BERTopic(
        embedding_model=embedding_model,
        nr_topics=40,
        verbose=True
    )

    print("Training BERTopic model...")
    topics, probs = topic_model.fit_transform(docs)
    topic_model.reduce_topics(docs, nr_topics=40)

    print("Generating topic labels with Ollama (local, no rate limits)...")
    topic_info = topic_model.get_topic_info()
    
    all_rep_docs = topic_model.representative_docs_ 
    
    centroids = {}
    topic_labels = {}

    for _, row in topic_info.iterrows():
        topic_id = row['Topic']
        if topic_id == -1: 
            continue
        
        try:
            topic_words = topic_model.get_topic(topic_id)
            keywords = [word for word, _ in topic_words][:10] if topic_words else []
        except Exception as e:
            print(f"Error getting keywords for topic {topic_id}: {e}")
            keywords = []
        
        rep_docs = all_rep_docs.get(topic_id, [])
        
        print(f"Labeling topic {topic_id}...")
        label = generate_topic_label_with_ollama(keywords, rep_docs)
        topic_labels[topic_id] = label
        print(f"  Topic {topic_id}: {label}")

        try:
            if rep_docs:
                embeddings = embedding_model.encode(rep_docs)
                centroid = np.mean(embeddings, axis=0)
                centroids[topic_id] = {
                    'label': label,
                    'centroid': centroid,
                    'keywords': keywords
                }
        except Exception as e:
            print(f"Error computing centroid for topic {topic_id}: {e}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    topic_model.save(str(MODEL_DIR / "bertopic_model"))

    with open(MODEL_DIR / "centroids.pkl", "wb") as f:
        pickle.dump(centroids, f)

    with open(MODEL_DIR / "topic_labels.json", "w") as f:
        json.dump(topic_labels, f, indent=2)

    print(f"\nTraining complete. Artifacts saved to {MODEL_DIR}.")
    print(f"Total topics with centroids: {len(centroids)}")
    print("\nTopic Labels:")
    for topic_id, label in topic_labels.items():
        print(f"  Topic {topic_id}: {label}")

if __name__ == "__main__":
    main()
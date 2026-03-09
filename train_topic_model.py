"""
train_topic_model_ollama.py - BERTopic training with LLM-assisted topic labeling.

Provides:
- Training BERTopic on a CSV dataset
- Extracting topic keyword clusters
- Generating professional topic labels using Ollama (Mistral)
- Computing topic centroids
- Saving model artifacts for inference

Pipeline:
1. Load documents from CSV dataset
2. Train BERTopic model (40 topics)
3. Extract keywords for each topic
4. Generate human-readable topic titles using Ollama
5. Compute embedding centroids for each topic
6. Save model artifacts for downstream inference

Requires:
- pandas                - load CSV dataset
- numpy                 - centroid computation
- bertopic              - topic modeling
- sentence-transformers - embedding generation
- umap-learn            - dimensionality reduction
- hdbscan               - clustering
- requests              - call Ollama API
- json                  - save artifacts
- os                    - filesystem operations

External Requirement:
- Ollama running locally
- Mistral model installed
  ollama run mistral

Input:
- data/topic_dataset.csv (must contain column: "text")

Output:
- models/bertopic_model/
- models/topic_keywords.json
- models/topic_labels.json
- models/topic_centroids.json

Run:
    python train_topic_model_ollama.py
"""

import os
import json
import pandas as pd
import numpy as np
import requests
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN

# Setup 
DATA_PATH = "data/topic_dataset.csv"
MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)

# Read dataset
df = pd.read_csv(DATA_PATH)
docs = df['text'].dropna().tolist()

# Train BERTopic
print("Training BERTopic model...")

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Intialize BERTopic
topic_model = BERTopic(
    embedding_model=embedding_model,
    umap_model=UMAP(
        n_neighbors=15, 
        n_components=5, 
        min_dist=0.0, 
        metric='cosine'
        ),
    hdbscan_model=HDBSCAN(
        min_cluster_size=10, 
        metric='euclidean', 
        prediction_data=True
        ),
    nr_topics=40,
    calculate_probabilities=True
)

# Training model
topics, _ = topic_model.fit_transform(docs)

# Extract and save keywords
print("Saving keywords to models/topic_keywords.json...")
topic_keywords_dict = {}
topic_info = topic_model.get_topic_info()

for topic_id in topic_info['Topic']:
    # Skip outlier topic
    if topic_id == -1:
        continue 
    
    # Extract keywords from BERTopic
    words = [word for word, score in topic_model.get_topic(topic_id)]
    topic_keywords_dict[str(topic_id)] = words

# Save keyword clusters
with open(os.path.join(MODEL_DIR, "topic_keywords.json"), "w", encoding="utf-8") as f:
    json.dump(topic_keywords_dict, f, indent=4)

# Generate topic labels (Ollama + Mistral)
print("Generating professional labels via Ollama (Mistral)...")
topic_labels_dict = {}

print("Refining topic labels...")

# Generate label for each topic using LLM
for topic_id, keywords in topic_keywords_dict.items():
    
    # Filter keywords 
    clean_keywords = [k for k in keywords if len(k) > 2][:6]

    # Filter out common nonsense/meaningless words 
    garbage_words = {'the', 'and', 'for', 'that', 'this', 'with', 'from', 'our', 'their', 'are'}
    clean_keywords = [k for k in keywords if k.lower() not in garbage_words][:6]
    
    # Prompt template for LLM
    prompt = f"""You are a professional editor. Your task is to turn raw keyword clusters into clean, business-ready topic titles.

    RULES:
    - Length: Exactly 2 to 3 words.
    - Tone: Academic, professional, and descriptive.
    - Avoid: Do NOT use "the", "or", "and" or "topic". Do NOT just repeat keywords.

    EXAMPLES:
    Keywords: [sun, earth, planet, space] -> Title: Planetary Systems in Universe
    Keywords: [sleep, rem, dreams, night] -> Title: Sleep Cycle
    Keywords: [people, psychological, person, tendency] -> Title: Psychological Phenomenon
    Keywords: [ocean, sea, water, blue] -> Title: Marine Environments
    Keywords: [mountains, plate, range, mount] -> Title: Geological Evolution

    CURRENT TASK:
    Keywords: {', '.join(clean_keywords)}
    Title:"""

    try:
        # Send request to local Ollama API
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "mistral", 
                "prompt": prompt, 
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=15
        )
        
        # Extract and clean response
        label = response.json().get("response", "").strip().strip('"').split('\n')[0]
        label = label.split(':')[-1].strip() # Clean "Title: Name" hallucinations
    except:
        # Fallback label if Ollama fails
        label = " ".join(clean_keywords[:2]).title() # Fallback to first two keywords

    topic_labels_dict[topic_id] = label
    print(f"Topic {topic_id}: {label}")

# Save generated labels
with open(os.path.join(MODEL_DIR, "topic_labels.json"), "w", encoding="utf-8") as f:
    json.dump(topic_labels_dict, f, indent=4)

# Compute Topic Centroids & Save Model Artifacts
print("Saving centroids and model artifacts...")

# Generate embeddings for all documents
all_embeddings = embedding_model.encode(
    docs,
    show_progress_bar=True
    )

# Compute centroid for each topic
centroids = {str(tid): np.mean(all_embeddings[[i for i, t in enumerate(topics) if t == tid]], axis=0).tolist() 
             for tid in set(topics) if tid != -1}

# Save centroids
with open(os.path.join(MODEL_DIR, "topic_centroids.json"), "w") as f:
    json.dump(centroids, f)

# Save trained BERTopic model
topic_model.save(os.path.join(MODEL_DIR, "bertopic_model"), serialization="safetensors")

print(f"\nSuccess! All artifacts saved in {MODEL_DIR}/")
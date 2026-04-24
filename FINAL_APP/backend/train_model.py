import os
import re
import pickle
import numpy as np
import pandas as pd
import requests
import torch
import json
import sys
from unittest.mock import MagicMock

# Workaround for HDBSCAN package conflict (blocked DLLs)
# BERTopic internally checks for hdbscan even when using KMeans
try:
    import hdbscan
except Exception:
    mock_hdbscan = MagicMock()
    mock_hdbscan.HDBSCAN = type('HDBSCAN', (), {})
    sys.modules['hdbscan'] = mock_hdbscan

from tqdm import tqdm
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import CountVectorizer
from concurrent.futures import ThreadPoolExecutor

# =============================
# PATHS (Integrated with Project structure)
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "custom_dataset.csv")
from core.config import MODEL_DIR, OLLAMA_URL
OLLAMA_MODEL = "qwen2.5:3b"

# =============================
# UTILITIES
# =============================
def clean_text(text):
    """Clean HTML tags, multiple spaces, and normalize text."""
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove HTML entities like &lt; &gt;
    text = re.sub(r'&[a-z]+;', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def check_ollama():
    """Verify if Ollama is running and the model is available."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            if any(OLLAMA_MODEL in m for m in models):
                return True
            print(f"Warning: Model '{OLLAMA_MODEL}' not found in Ollama. Labeling will use defaults.")
            return False
        return False
    except:
        print("Warning: Ollama service not reachable. Labeling will be skipped.")
        return False

# =============================
# LOAD DATASETS (Supports Multiple CSVs)
# =============================
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

print(f"Scanning for datasets in {DATA_DIR}...")
csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

if not csv_files:
    print(f"Error: No .csv files found in {DATA_DIR}.")
    print("Please place your training data (e.g., custom_dataset.csv) in that folder.")
    exit()

all_documents = []
for file in csv_files:
    file_path = os.path.join(DATA_DIR, file)
    print(f"Reading {file}...")
    try:
        # Using low_memory=True for large files
        df = pd.read_csv(file_path, low_memory=True)
        if "text" in df.columns:
            print(f"  - Cleaning {len(df)} documents...")
            docs = df["text"].dropna().astype(str).apply(clean_text).tolist()
            # Filter out very short documents
            docs = [d for d in docs if len(d.split()) > 3]
            all_documents.extend(docs)
            print(f"  - Added {len(docs)} valid documents")
        else:
            print(f"  - Skipping {file}: No 'text' column found.")
    except Exception as e:
        print(f"  - Error reading {file}: {e}")

if not all_documents:
    print("Error: No valid documents found in any of the CSV files.")
    exit()

print(f"Total training set size: {len(all_documents)} documents")
documents = all_documents

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

hdbscan_model = KMeans(
    n_clusters=30, # Pre-defining clusters for stability
    random_state=42
)

# Added vectorizer for stopwords
vectorizer_model = CountVectorizer(stop_words="english")

# =============================
# INITIALIZE BERTopic
# =============================
topic_model = BERTopic(
    embedding_model=embedding_model,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    vectorizer_model=vectorizer_model,
    calculate_probabilities=True,
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
# SAVE MODEL (Using BERTopic native save)
# =============================
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_SAVE_PATH = os.path.join(MODEL_DIR, "bertopic_model")

try:
    topic_model.save(MODEL_SAVE_PATH, serialization="pickle")
    print(f"Model saved to {MODEL_SAVE_PATH}")
except Exception as e:
    print(f"Model saving error: {e}")

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
        label = response.json().get("response", "").strip().replace('"', '').replace("'", "")
        return label if label else "Unknown Topic"
    except Exception as e:
        print(f"Ollama error: {e}")
        return "Unknown Topic"

print("Extracting representative documents and generating labels (Parallel)...")
topic_info = topic_model.get_document_info(documents)
topic_labels = {}
centroids = {}

unique_topics = [tid for tid in topic_info["Topic"].unique() if tid != -1]

def process_topic(topic_id):
    docs = topic_info[topic_info["Topic"] == topic_id]["Document"].head(5).tolist()
    try:
        topic_words = topic_model.get_topic(topic_id)
        keywords = [word for word, _ in topic_words[:10]] if topic_words else []
    except:
        keywords = []
    
    label = generate_topic_label_with_ollama(keywords, docs)
    
    # Compute centroid
    centroid_data = None
    try:
        if docs:
            embs = embedding_model.encode(docs, batch_size=8, show_progress_bar=False)
            centroid = np.mean(embs, axis=0)
            centroid = normalize([centroid])[0]
            centroid_data = {"label": label, "centroid": centroid}
    except Exception as e:
        print(f"Centroid error for {topic_id}: {e}")
    
    return topic_id, label, centroid_data

print(f"Processing {len(unique_topics)} topics...")
ollama_available = check_ollama()

with ThreadPoolExecutor(max_workers=4) as executor:
    if ollama_available:
        results = list(tqdm(executor.map(process_topic, unique_topics), total=len(unique_topics), desc="Labeling"))
    else:
        # Fallback to simple labeling if Ollama is down
        results = [(tid, f"Topic {tid}", None) for tid in unique_topics]
    
    for tid, lbl, cd in results:
        topic_labels[tid] = lbl
        if cd:
            centroids[tid] = cd

# =============================
# SAVE ARTIFACTS
# =============================
print("Saving artifacts...")
try:
    with open(os.path.join(MODEL_DIR, "topic_centroids.pkl"), "wb") as f:
        pickle.dump(centroids, f)

    with open(os.path.join(MODEL_DIR, "topic_labels.pkl"), "wb") as f:
        pickle.dump(topic_labels, f)

    # Export extra JSON for readability
    simple_labels = [{"id": int(tid), "label": lbl} for tid, lbl in topic_labels.items()]
    with open(os.path.join(MODEL_DIR, "topic_labels.json"), "w", encoding="utf-8") as f:
        json.dump(simple_labels, f, indent=4)

    print("Pipeline complete. Model and artifacts are ready for the main application.")
except Exception as e:
    print(f"Saving artifacts error: {e}")

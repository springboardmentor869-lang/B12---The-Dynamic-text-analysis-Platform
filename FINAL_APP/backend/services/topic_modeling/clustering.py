import os
import sys
import pickle
import numpy as np
import pandas as pd
from unittest.mock import MagicMock

# Workaround for HDBSCAN package conflict (blocked DLLs)
# BERTopic internally checks for hdbscan even when using KMeans
try:
    import hdbscan
except Exception:
    mock_hdbscan = MagicMock()
    mock_hdbscan.HDBSCAN = type('HDBSCAN', (), {})
    sys.modules['hdbscan'] = mock_hdbscan

from bertopic import BERTopic
from umap import UMAP
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer

from core.config import MODEL_DIR
from services.topic_modeling.embeddings import get_embedding_model
from services.topic_modeling.labeling import refine_topic_labels
from concurrent.futures import ThreadPoolExecutor

MODEL_PATH = os.path.join(MODEL_DIR, "bertopic_model")
LABELS_PATH = os.path.join(MODEL_DIR, "topic_labels.pkl")


def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    
    # BERTopic native load is safer than pickle
    try:
        return BERTopic.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading topic model: {e}. Model might be incompatible. Re-training will be triggered.")
        return None


def load_labels():
    if not os.path.exists(LABELS_PATH):
        return None
    
    with open(LABELS_PATH, "rb") as f:
        return pickle.load(f)


def train_model(chunks, documents_for_training=None):
    """
    Train BERTopic using user's sophisticated settings.
    'chunks' are for current context, 'documents_for_training' can be used for initial setup.
    """
    print("Training BERTopic model with UMAP + HDBSCAN...")

    embedding_model = get_embedding_model()
    
    # 1. Dimensionality Reduction (UMAP)
    umap_model = UMAP(
        n_neighbors=15, 
        n_components=5, 
        min_dist=0.0, 
        metric="cosine"
    )

    # 2. Clustering (KMeans) - More stable for prediction on Windows
    hdbscan_model = KMeans(n_clusters=30, random_state=42) 

    # 3. Vectorizer (Stopwords)
    vectorizer_model = CountVectorizer(stop_words="english")

    # 4. Initialize
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        calculate_probabilities=True,
        verbose=True
    )

    # 5. Fit
    docs = documents_for_training if documents_for_training else chunks
    topics, probs = topic_model.fit_transform(docs)

    # 6. Reduce Topics if necessary
    if len(topic_model.get_topics()) > 40:
        topic_model.reduce_topics(docs, nr_topics=40)

    # 7. Save Model
    os.makedirs(MODEL_DIR, exist_ok=True)
    topic_model.save(MODEL_PATH, serialization="pickle")

    # 8. Generate and Save Labels (Parallel Ollama Integration)
    print("Generating labels for new model in parallel...")
    topic_info = topic_model.get_document_info(docs)
    topic_labels = {}
    
    unique_topics = [tid for tid in topic_info["Topic"].unique() if tid != -1]
    
    def get_label(topic_id):
        representative_docs = topic_info[topic_info["Topic"] == topic_id]["Document"].head(5).tolist()
        topic_words = topic_model.get_topic(topic_id)
        keywords = [word for word, _ in topic_words[:10]] if topic_words else []
        label = refine_topic_labels(topic_id, keywords, representative_docs)
        return topic_id, label

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(get_label, unique_topics))
        for tid, lbl in results:
            topic_labels[tid] = lbl

    with open(LABELS_PATH, "wb") as f:
        pickle.dump(topic_labels, f)

    return topic_model, topics, probs


def extract_topics(chunks, task_manager=None, task_id=None):
    """
    Main function used by pipeline
    """
    if task_manager and task_id:
        task_manager.update_progress(task_id, "Loading topic models...", 20)

    model = load_model()
    labels = load_labels()

    if model is None:
        if task_manager and task_id:
            task_manager.update_progress(task_id, "Training new topic model (UMAP+HDBSCAN)...", 25)
        model, topics, probs = train_model(chunks)
    else:
        if task_manager and task_id:
            task_manager.update_progress(task_id, "Predicting topics...", 40)
        topics, probs = model.transform(chunks)

    topic_info = model.get_topic_info()

    # Convert topic info to dict
    topic_details = {}
    for _, row in topic_info.iterrows():
        topic_id = int(row["Topic"])
        raw_name = str(row["Name"])
        
        # Use LLM-refined label if it exists in the pkl
        clean_label = labels.get(topic_id, raw_name) if labels else raw_name
        
        topic_details[topic_id] = {
            "count": int(row["Count"]),
            "name": raw_name,
            "label": clean_label
        }

    # Chunk mapping
    chunk_results = []
    for i, chunk in enumerate(chunks):
        chunk_results.append({
            "chunk": chunk[:200],
            "topic_id": int(topics[i])
        })

    return {
        "num_topics": len(topic_details),
        "topics": topic_details,
        "chunks": chunk_results
    }
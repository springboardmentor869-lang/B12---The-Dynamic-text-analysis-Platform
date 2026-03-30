import os
import json
import time
import requests
import numpy as np
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
from bertopic import BERTopic
from sklearn.datasets import fetch_20newsgroups

#  Local LLM Setup (Ollama) ---
# Ensure you have run: ollama run qwen2.5:1.5b
OLLAMA_MODEL = "qwen2.5:1.5b"
OLLAMA_URL = "http://localhost:11434/api/generate"

def get_llm_topic_label(keywords, rep_docs):
    """Generates human-readable topic labels using Ollama (Mentor Requirement #4)"""
    prompt = f"""
    TASK: Generate a concise, human-readable label (2-4 words) for a topic based on these keywords and text.
    KEYWORDS: {', '.join(keywords)}
    REPRESENTATIVE TEXT: {rep_docs[0][:300]}...
    
    Return ONLY the short label. No quotes, no explanations.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0}},
            timeout=60
        )
        return response.json().get("response", "").strip()
    except Exception:
        return " & ".join([k.capitalize() for k in keywords[:2]])

def main():
    # #1: Dataset of ~1000 documents ---
    print("Loading ~1000 diverse documents...")
    dataset = fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'), random_state=42)
    docs = [doc for doc in dataset.data if len(doc.split()) > 20][:1000]

    print("\nConfiguring BERTopic pipeline (Mentor Requirement #2)...")
    
    # #2: Embedding, UMAP, HDBSCAN ---
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2") 

    
    # FIX 1: Lower n_neighbors so UMAP looks for tiny, local patterns
    umap_model = umap.UMAP(
        n_neighbors=5, 
        n_components=5, 
        min_dist=0.0, 
        metric='cosine', 
        random_state=42
    )
    
    # FIX 2: Lower cluster requirements and use 'leaf' to find micro-topics
    hdbscan_model = hdbscan.HDBSCAN(
        min_cluster_size=5,       # If only 5 docs match, it's a topic (Prevents Topic -1)
        min_samples=1,            # Be extremely forgiving
        metric='euclidean', 
        cluster_selection_method='leaf', # Forces discovery of small clusters
        prediction_data=True
    )

    # --- MENTOR REQUIREMENT #3: Train and Reduce to 40 topics ---
    print("\nTraining initial model...")
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        verbose=True
    )

    topics, probs = topic_model.fit_transform(docs)
    
    print(f"Initial clusters found: {len(topic_model.get_topic_info()) - 1}")
    print("Forcing reduction to 40 topics...")
    topic_model.reduce_topics(docs, nr_topics=40)

    topic_info = topic_model.get_topic_info()
    
    print("\nGenerating LLM Labels and Computing Centroids (Mentor Requirement #4 & #5)...")
    topic_mapping = {}
    centroids = {}

    for index, row in topic_info.iterrows():
        topic_id = row['Topic']
        if topic_id == -1: continue

        # Get keywords and representative docs for the LLM
        top_words = [word for word, score in topic_model.get_topic(topic_id)[:5]]
        rep_docs = topic_model.get_representative_docs(topic_id)
        
        # Labeling via local AI
        label = get_llm_topic_label(top_words, rep_docs)
        topic_mapping[str(topic_id)] = label
        print(f"Topic {topic_id}: {label}")

        #  #5: Compute Centroids (Avg Embeddings) ---
        rep_embeddings = embedding_model.encode(rep_docs)
        centroid = np.mean(rep_embeddings, axis=0)
        centroids[str(topic_id)] = centroid.tolist()

    # : Save Artifacts in models/ ---
    print("\nSaving artifacts to models/ directory...")
    os.makedirs("models", exist_ok=True)
    
    with open("models/topic_mapping.json", "w", encoding="utf-8") as f:
        json.dump(topic_mapping, f, indent=4)
        
    with open("models/topic_centroids.json", "w", encoding="utf-8") as f:
        json.dump(centroids, f)

    print("✅ Offline Training Complete!")

if __name__ == "__main__":
    main()
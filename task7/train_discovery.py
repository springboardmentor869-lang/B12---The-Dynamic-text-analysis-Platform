import os
import json
import time
import numpy as np
import pandas as pd
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
from bertopic import BERTopic
from dotenv import load_dotenv

# --- DATASET UTILITIES ---
from sklearn.datasets import fetch_20newsgroups
from datasets import load_dataset

load_dotenv()

# --- LLM CONFIGURATION ---
# Using OpenRouter to provide human-readable labels for abstract mathematical clusters
import os
from openai import OpenAI

# Update your client setup
client = OpenAI(
    base_url="https://api.x.ai/v1",  # <--- Change this to xAI's endpoint
    api_key=os.getenv("GROK_API_KEY")
)

def get_llm_topic_label(keywords, rep_docs):
    """Generates labels using Grok 4.1 Fast."""
    prompt = f"""
    TASK: Generate a concise, human-readable label (2-4 words) for a topic. Keep the label professional and academic.
    KEYWORDS: {', '.join(keywords)}
    REPRESENTATIVE TEXT: {rep_docs[0][:300]}...
    
    Return ONLY the short label.
    """
    try:
        response = client.chat.completions.create(
            model="grok-4.1-fast", # <--- Use the 2026 high-speed model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Grok Error: {e}")
        return "Unknown Topic"

def load_dynamic_mega_dataset():
    """
    NLP Phase: Data Ingestion & Diversification.
    Combines '20 Newsgroups' (general world knowledge) with 'EDGAR' (corporate financial knowledge).
    This ensures the 'Dynamic' platform can handle everything from sports to SEC filings.
    """
    print("1. Loading General Knowledge (News, Tech, Sports, etc.)...")
    news_dataset = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'))
    general_docs = [doc for doc in news_dataset.data if len(doc.strip()) > 50]
    
    print("2. Loading Corporate/Financial Knowledge...")
    try:
        # Pulling 3,000 sections from real SEC filings to teach the model financial jargon
        fin_dataset = load_dataset("eloukas/edgar-corpus", "financial_section", split="train[:3000]")
        financial_docs = [doc['text'] for doc in fin_dataset if len(doc['text']) > 50]
    except Exception as e:
        print(f"Warning: Could not load HuggingFace dataset. {e}")
        financial_docs = []

    # Merging both worlds into a single training corpus
    combined_docs = general_docs + financial_docs
    print(f"Total documents for dynamic training: {len(combined_docs)}")
    
    return combined_docs

def main():
    # Step 1: Load the mixed-domain corpus
    docs = load_dynamic_mega_dataset()

    print("\nConfiguring BERTopic pipeline...")
    
    # Step 2: Embedding (Phase 1 & 2)
    # Using 'all-mpnet-base-v2' - a powerful generalist model that understands context
    embedding_model = SentenceTransformer("all-mpnet-base-v2") 
    
    # Step 3: Dimensionality Reduction (UMAP)
    # Squishes 768-dim vectors into 5-dim space while preserving semantic clumps
    umap_model = umap.UMAP(n_neighbors=5, min_dist=0.01, metric='cosine', random_state=42)
    
    # Step 4: Clustering (HDBSCAN)
    # Identifies dense 'islands' of data points. min_cluster_size determines topic granularity.
    hdbscan_model = hdbscan.HDBSCAN(
        min_cluster_size=15, 
        min_samples=5, 
        metric='euclidean', 
        cluster_selection_method='eom', 
        prediction_data=True
    )
    
    # Step 5: The BERTopic Wrapper
    # nr_topics="auto" allows the model to naturally discover the number of themes
    print("\nTraining model and dynamically finding topics...")
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        nr_topics=40, 
        verbose=True
    )

    # Execute the training pipeline
    topics, probabilities = topic_model.fit_transform(docs)
    topic_info = topic_model.get_topic_info()
    
    print(f"\nModel trained! Active topics found: {len(topic_info) - 1}")
    print("Generating LLM Labels and Computing Centroids...")
    
    topic_mapping = {}
    centroids = {}

    # Step 6: Post-Processing Artifacts
    # We iterate through the discovered clusters to create our 'Inference Map'
    for index, row in topic_info.iterrows():
        topic_id = row['Topic']
        if topic_id == -1:
            continue # Topic -1 is the 'Noise' cluster (outliers)

        # Retrieve top keywords (via C-TF-IDF) and the best examples of this topic
        top_words = [word for word, score in topic_model.get_topic(topic_id)[:5]]
        rep_docs = topic_model.get_representative_docs(topic_id)
        
        # Call LLM to give the cluster a name (e.g., 'Annual Financial Results')
        human_label = get_llm_topic_label(top_words, rep_docs)
        topic_mapping[str(topic_id)] = human_label
        print(f"Topic {topic_id}: {human_label}")
        time.sleep(4) # Rate limiting for OpenRouter free tier
        
        # Calculate the mathematical 'Center' (Centroid) of the topic island
        # This allows for lightning-fast matching in the backend later
        rep_embeddings = embedding_model.encode(rep_docs)
        centroid = np.mean(rep_embeddings, axis=0)
        centroids[str(topic_id)] = centroid.tolist()

    # Step 7: Save Results
    # These artifacts allow the FastAPI backend to run without re-training the whole model
    print("\nSaving artifacts to models/ directory...")
    os.makedirs("models", exist_ok=True)
    
    with open("models/topic_mapping.json", "w", encoding="utf-8") as f:
        json.dump(topic_mapping, f, indent=4)
        
    with open("models/topic_centroids.json", "w", encoding="utf-8") as f:
        json.dump(centroids, f)

    print("Offline Training Complete! Model artifacts are ready for inference.")

if __name__ == "__main__":
    main()
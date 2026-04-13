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

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={"HTTP-Referer": "http://localhost:3000"}
)

def get_llm_topic_label(keywords, rep_docs):
    """Generates human-readable topic labels using an LLM by analyzing keywords and representative docs."""
    prompt = f"""
    TASK: Generate a concise, human-readable label (2-4 words) for a financial/business topic based on these keywords and text.
    KEYWORDS: {', '.join(keywords)}
    REPRESENTATIVE TEXT: {rep_docs[0][:300]}...
    
    Return ONLY the short label. No quotes, no explanations.
    """
    try:
        response = client.chat.completions.create(
            model="openrouter/free", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Unknown Topic"

def load_custom_dataset(csv_path):
    print(f"Loading custom data from {csv_path}...")
    df = pd.read_csv(csv_path, header=None, names=['sentiment', 'text'], encoding='latin-1')
    
    docs = df['text'].dropna().astype(str).tolist()
    docs = docs[:1000]
    
    print(f"Loaded {len(docs)} documents for training.")
    return docs

def main():
    docs = load_custom_dataset("financial.csv")

    print("\nConfiguring BERTopic pipeline...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2") 
    umap_model = umap.UMAP(n_neighbors=5, min_dist=0.01, metric='cosine', random_state=42)
    hdbscan_model = hdbscan.HDBSCAN(
        min_cluster_size=15, 
        min_samples=5, 
        metric='euclidean', 
        cluster_selection_method='eom', 
        prediction_data=True
    )
    print("\nTraining model and reducing to 40 topics...")
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        nr_topics=40,
        verbose=True
    )

    topics, probabilities = topic_model.fit_transform(docs)
    topic_info = topic_model.get_topic_info()
    
    print(f"\nModel trained! Active topics remaining: {len(topic_info) - 1}")
    print("Generating LLM Labels and Computing Centroids...")
    
    topic_mapping = {}
    centroids = {}

    for index, row in topic_info.iterrows():
        topic_id = row['Topic']
        if topic_id == -1:
            continue # Skip the noise cluster

        top_words = [word for word, score in topic_model.get_topic(topic_id)[:5]]
        rep_docs = topic_model.get_representative_docs(topic_id)
        
        # 1. Generate Label
        human_label = get_llm_topic_label(top_words, rep_docs)
        topic_mapping[str(topic_id)] = human_label
        print(f"Topic {topic_id}: {human_label}")
        time.sleep(4) # Respect OpenRouter rate limits
        
        rep_embeddings = embedding_model.encode(rep_docs)
        centroid = np.mean(rep_embeddings, axis=0)
        centroids[str(topic_id)] = centroid.tolist()

    print("\nSaving artifacts to models/ directory...")
    print("\nSaving artifacts to models/ directory...")
    os.makedirs("models", exist_ok=True)
    
    with open("models/topic_mapping.json", "w", encoding="utf-8") as f:
        json.dump(topic_mapping, f, indent=4)
        
    with open("models/topic_centroids.json", "w", encoding="utf-8") as f:
        json.dump(centroids, f)

    print("Offline Training Complete! Model artifacts are ready for inference.")

if __name__ == "__main__":
    main()
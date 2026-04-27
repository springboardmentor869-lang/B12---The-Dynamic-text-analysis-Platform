import sys
import os
import json
import pandas as pd
import numpy as np
import time
import requests
import warnings
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN

# Force output buffering off
sys.stdout.flush()
sys.stderr.flush()
warnings.filterwarnings('ignore')

# ─── CONFIG ───────────────────────────────────────────────
DATA_PATH = "topic_dataset.csv"
MODEL_DIR = "models"
NUM_TOPICS = 40

os.makedirs(MODEL_DIR, exist_ok=True)

# ─── OLLAMA CONFIG ────────────────────────────────────────
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "mistral"
USE_LLM = True  # Set to False to skip LLM generalization

# ─── STEP 1: LOAD DATA ────────────────────────────────────
print("\n" + "=" * 70, flush=True)
print("STEP 1: LOADING DATA", flush=True)
print("=" * 70, flush=True)

try:
    df = pd.read_csv(DATA_PATH)
    docs = df['text'].dropna().astype(str).tolist()
    print(f"  Loaded {len(docs)} documents\n", flush=True)
except Exception as e:
    print(f"  ERROR loading data: {e}", flush=True)
    sys.exit(1)

if len(docs) < 500:
    print(f"WARNING: Dataset < 500 docs ({len(docs)} found)", flush=True)
    print("   Recommendation: Collect at least 1,000 documents.\n", flush=True)

# ─── STEP 2: LOAD EMBEDDING MODEL ────────────────────────
print("=" * 70, flush=True)
print("STEP 2: LOADING EMBEDDING MODEL", flush=True)
print("=" * 70, flush=True)

try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✓ Loaded: all-MiniLM-L6-v2\n", flush=True)
except Exception as e:
    print(f"✗ ERROR loading embedding model: {e}", flush=True)
    sys.exit(1)

# ─── STEP 3: TRAIN BERTOPIC ───────────────────────���──────
print("=" * 70, flush=True)
print("STEP 3: TRAINING BERTOPIC", flush=True)
print("=" * 70, flush=True)
print(f"Target: {NUM_TOPICS} topics from {len(docs)} documents\n", flush=True)

try:
    umap_model = UMAP(
        n_neighbors=15,
        n_components=5,
        min_dist=0.0,
        metric='cosine',
        random_state=42
    )

    hdbscan_model = HDBSCAN(
        min_cluster_size=10,
        metric='euclidean',
        prediction_data=True
    )

    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        nr_topics=NUM_TOPICS,
        top_n_words=10,
        calculate_probabilities=True,
        verbose=False
    )

    print("Training... (this may take several minutes)", flush=True)
    start = time.time()
    topics, probs = topic_model.fit_transform(docs)
    elapsed = time.time() - start

    unique_topics = len(set(topics)) - (1 if -1 in topics else 0)
    outliers = sum(1 for t in topics if t == -1)
    outlier_pct = 100 * outliers / len(docs)

    print(f"  Complete in {elapsed:.1f}s", flush=True)
    print(f"  Topics: {unique_topics}/{NUM_TOPICS}", flush=True)
    print(f"  Outliers: {outliers} ({outlier_pct:.1f}%)\n", flush=True)
    
except Exception as e:
    print(f"  ERROR during training: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ─── STEP 4: EXTRACT KEYWORDS ────────────────────────────
print("=" * 70, flush=True)
print("STEP 4: EXTRACTING KEYWORDS & INITIAL LABELS", flush=True)
print("=" * 70, flush=True)

try:
    topic_info = topic_model.get_topic_info()

    garbage_words = {
        'the', 'and', 'for', 'that', 'this', 'with', 'from', 'are', 'is',
        'a', 'an', 'to', 'of', 'in', 'on', 'at', 'by', 'as', 'or', 'but',
        'its', 'it', 'be', 'been', 'have', 'has', 'do', 'does', 'did',
        'was', 'were', 'am', 'also', 'can', 'very', 'they', 'their', 'more',
        'just', 'like', 'way', 'time', 'thing', 'day', 'year', 'people',
        'one', 'two', 'would', 'could', 'should', 'such', 'which'
    }

    topic_keywords = {}
    initial_labels = {}

    for topic_id in topic_info['Topic']:
        if topic_id == -1:
            continue
        
        raw_keywords = topic_model.get_topic(topic_id)
        
        keywords = [
            word for word, score in raw_keywords
            if score > 0.01 and 3 <= len(word) <= 20 and word.lower() not in garbage_words
        ][:10]
        
        # Initial label from keywords
        if len(keywords) >= 2:
            initial_label = f"{keywords[0].title()} {keywords[1].title()}"
        elif len(keywords) == 1:
            initial_label = keywords[0].title()
        else:
            initial_label = f"Topic {topic_id}"
        
        topic_keywords[str(topic_id)] = keywords
        initial_labels[str(topic_id)] = initial_label

    print(f"  Extracted keywords for {len(topic_keywords)} topics\n", flush=True)

except Exception as e:
    print(f"  ERROR extracting keywords: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ─── STEP 5: GENERALIZE LABELS WITH LLM ─────────────────
print("=" * 70, flush=True)
print("STEP 5: GENERALIZING LABELS WITH LLM", flush=True)
print("=" * 70, flush=True)

def call_ollama(prompt):
    """Call Ollama API."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.35}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            return result if result else None
        return None
            
    except Exception as e:
        return None

if USE_LLM:
    print("Contacting LLM for label generalization...\n", flush=True)
    generalized_labels = {}
    success_count = 0
    
    for topic_id_str in sorted([k for k in initial_labels.keys()], key=lambda x: int(x)):
        topic_id = int(topic_id_str)
        initial_label = initial_labels[topic_id_str]
        topic_kws = topic_keywords[topic_id_str][:8]
        
        prompt = f"""You are an expert at generalizing research topic labels into broader academic fields.

Given a topic label and keywords, suggest a MORE GENERAL category name:
1. Broader field (not specific examples)
2. Established academic field when possible
3. 1-3 words, professional and clear
4. Avoid vague terms like "General", "Miscellaneous", "Other"

EXAMPLES:
"Metal Material" [metal, gold] → Materials Science
"Babies Child" [baby, infant, reflex] → Developmental Biology
"Ocean Sea" [ocean, sea, marine] → Marine Science
"Space Planet" [space, planet, star] → Astronomy
"Building Construction" [construction, urban, building] → Architecture

---

Topic: "{initial_label}"
Keywords: {topic_kws}

Respond with ONLY the generalized category (1-4 words):"""

        llm_suggestion = call_ollama(prompt)
        
        if llm_suggestion:
            suggestion = llm_suggestion.strip().strip('"').split('\n')[0].strip()
            
            word_count = len(suggestion.split())
            if 1 <= word_count <= 4 and 2 < len(suggestion) < 50:
                generalized_labels[topic_id_str] = suggestion
                success_count += 1
            else:
                generalized_labels[topic_id_str] = initial_label
                suggestion = initial_label
        else:
            generalized_labels[topic_id_str] = initial_label
            suggestion = initial_label
        
        print(f"{topic_id:2d}: {initial_label:25s} \nLabel : {suggestion}", flush=True)
        time.sleep(0.1)  # Rate limit
    
    final_labels = generalized_labels
    print(f"\n  {success_count}/{len(initial_labels)} labels generalized\n", flush=True)
else:
    final_labels = initial_labels
    print("LLM generalization skipped (USE_LLM=False)\n", flush=True)

# ─── STEP 6: COMPUTE CENTROIDS ───────────────────────────
print("=" * 70, flush=True)
print("STEP 6: COMPUTING CENTROIDS", flush=True)
print("=" * 70, flush=True)

try:
    print("Encoding documents...", flush=True)
    all_embeddings = embedding_model.encode(docs, show_progress_bar=True)

    print("Computing centroids...", flush=True)
    centroids = {}

    for topic_id in topic_info['Topic']:
        if topic_id == -1:
            continue
        
        topic_doc_indices = [i for i, t in enumerate(topics) if t == topic_id]
        
        if len(topic_doc_indices) > 0:
            topic_embeddings = all_embeddings[topic_doc_indices]
            centroid = np.mean(topic_embeddings, axis=0)
            centroids[str(topic_id)] = centroid.tolist()

    print(f"  Computed {len(centroids)} centroids\n", flush=True)

except Exception as e:
    print(f"  ERROR computing centroids: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ─── STEP 7: SAVE ARTIFACTS ──────────────────────────────
print("=" * 70, flush=True)
print("STEP 7: SAVING ARTIFACTS", flush=True)
print("=" * 70, flush=True)

try:
    # Save labels
    labels_path = os.path.join(MODEL_DIR, "topic_labels.json")
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump(final_labels, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {labels_path}", flush=True)

    # Save keywords
    keywords_path = os.path.join(MODEL_DIR, "topic_keywords.json")
    with open(keywords_path, "w", encoding="utf-8") as f:
        json.dump(topic_keywords, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {keywords_path}", flush=True)

    # Save centroids
    centroids_path = os.path.join(MODEL_DIR, "topic_centroids.json")
    with open(centroids_path, "w") as f:
        json.dump(centroids, f)
    print(f"  Saved: {centroids_path}", flush=True)

    # Save model
    model_path = os.path.join(MODEL_DIR, "bertopic_model")
    topic_model.save(model_path, serialization="safetensors")
    print(f"  Saved: {model_path}/", flush=True)

except Exception as e:
    print(f"  ERROR saving artifacts: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ─── SUMMARY ──────────────────────────────────────────────
print("\n" + "=" * 70, flush=True)
print("  COMPLETE", flush=True)
print("=" * 70, flush=True)
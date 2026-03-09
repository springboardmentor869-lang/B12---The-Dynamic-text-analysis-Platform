"""
inference.py - document topic classification pipeline.

Provides:
- Automatic parsing of documents (PDF / DOCX)
- Text extraction using configured parsers
- Topic inference using a trained BERTopic model
- Mapping topic IDs to professional labels
- Saving extracted text cache and classification results

Pipeline:
1. Load trained BERTopic model and topic labels
2. Parse documents from dataset folder
3. Extract text using appropriate parser
4. Cache extracted text for reuse
5. Perform topic classification
6. Map topic ID → human-readable label
7. Save results to JSON report

Requires:
- bertopic              - topic modeling inference
- sentence-transformers - embedding generation
- parsers.py            - document parsing utilities
- json                  - saving results
- os                    - file system operations

Supported Parsers (via parsers.PARSERS):
- docx      - DOCX parser
- pymupdf   - PDF text extraction
- ocr       - OCR fallback for scanned PDFs

Input:
- dataset/*.pdf
- dataset/*.docx

Model Artifacts Required:
- models/bertopic_model/
- models/topic_labels.json

Output:
- results/text_cache/*.txt
- results/classification_results.json

Run:
    python inference.py
"""

import os
import json
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from parsers import PARSERS 

# Setup
MODEL_PATH = "models/bertopic_model"
LABELS_PATH = "models/topic_labels.json"
DATASET_DIR = "dataset"
RESULTS_DIR = "results"
CACHE_DIR = os.path.join(RESULTS_DIR, "text_cache")

# Create results folders
os.makedirs(CACHE_DIR, exist_ok=True)

# Load model and topic labels
print("Loading Intelligence Assets...")

# Load embedding model used by BERTopic
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load trained BERTopic model
model = BERTopic.load(MODEL_PATH, embedding_model=embedding_model)

# Load topic label mapping
with open(LABELS_PATH, "r", encoding="utf-8") as f:
    topic_labels = json.load(f)

classification_output = []

# Process documents
print(f"Processing documents in {DATASET_DIR}...")

for file_name in os.listdir(DATASET_DIR):
    path = os.path.join(DATASET_DIR, file_name)
    text = ""

    # Extension check
    ext = file_name.lower()
    if ext.endswith(".docx"):
        text = PARSERS["docx"](path)
    elif ext.endswith(".pdf"):
        text = PARSERS["pymupdf"](path)
        if not text.strip():
            print(f"Empty text layer in {file_name}. Switching to OCR...")
            text = PARSERS["ocr"](path)
    
    if text.strip():
        # Save the extracted text to cache
        txt_filename = f"{file_name}.txt"
        with open(os.path.join(CACHE_DIR, txt_filename), "w", encoding="utf-8") as f:
            f.write(text)
        
        # Proceed to labeling
        topics, _ = model.transform([text])
        topic_id = str(topics[0])
        label = topic_labels.get(topic_id, f"Topic {topic_id}")

        print(f"File: {file_name} -> Label: {label}")

        # Store result for JSON output
        classification_output.append({
            "file": file_name,
            "text_file": txt_filename,
            "topic_id": topic_id,
            "label": label
        })

# Save final results
with open(os.path.join(RESULTS_DIR, "classification_results.json"), "w", encoding="utf-8") as f:
    json.dump(classification_output, f, indent=4)

print(f"\nFinished! Results saved in {RESULTS_DIR}")
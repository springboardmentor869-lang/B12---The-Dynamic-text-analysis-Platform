"""
api_topic_classifier.py - FastAPI endpoint for document topic classification.

Provides:
- REST API endpoint to upload documents (PDF/DOCX)
- Extract text using parsers (docx / pymupdf / OCR fallback)
- Perform topic classification using trained BERTopic model
- Map topic ID to human-readable label
- Cache extracted text for reuse

Endpoint:
- POST /classify-file

Pipeline:
1. Receive uploaded file
2. Save file temporarily
3. Extract text using appropriate parser
4. Fallback to OCR if PDF has no text layer
5. Cache extracted text
6. Perform topic inference using BERTopic
7. Map topic ID → label
8. Return classification result

Requires:
- fastapi               - API framework
- shutil                - file handling
- os                    - filesystem operations
- json                  - load topic labels
- bertopic              - topic modeling inference
- sentence-transformers - embeddings
- parsers.py            - document parsing utilities

Model Artifacts Required:
- models/bertopic_model/
- models/topic_labels.json

Input:
- Multipart file upload (.pdf or .docx)

Output:
- JSON response:
    {
        "filename": "...",
        "topic_id": "...",
        "label": "..."
    }

Cache Output:
- results/text_cache/*.txt

Run:
    uvicorn api:app --reload
"""

from fastapi import APIRouter, UploadFile, File
import os
import json
import shutil

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from parsers import PARSERS

router = APIRouter()

# Paths
MODEL_PATH = "models/bertopic_model"
LABELS_PATH = "models/topic_labels.json"
RESULTS_DIR = "results"
CACHE_DIR = os.path.join(RESULTS_DIR, "text_cache")

os.makedirs(CACHE_DIR, exist_ok=True)

# ✅ Load model ONCE
print("Loading Intelligence Assets...")

# Load embedding model for BERTopic
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# Load trained BERTopic model
model = BERTopic.load(MODEL_PATH, embedding_model=embedding_model)

# Load topic label mapping
with open(LABELS_PATH, "r", encoding="utf-8") as f:
    topic_labels = json.load(f)


# API Endpoint
@router.post("/classify-file")
async def classify_file(file: UploadFile = File(...)):

    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = ""

        # Extract text based on file type
        if file.filename.lower().endswith(".docx"):
            text = PARSERS["docx"](temp_path)

        elif file.filename.lower().endswith(".pdf"):
            text = PARSERS["pymupdf"](temp_path)

            if not text.strip():
                print(f"[OCR FALLBACK] {file.filename}")
                text = PARSERS["ocr"](temp_path)

        else:
            os.remove(temp_path)
            return {"error": "Unsupported file type"}

        # Check empty text
        if not text.strip():
            os.remove(temp_path)
            return {"error": "Could not extract text from file"}

        # Save cache
        txt_filename = f"{file.filename}.txt"
        cache_path = os.path.join(CACHE_DIR, txt_filename)

        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(text)

        # Topic inference
        topics, _ = model.transform([text])
        topic_id = str(topics[0])

        # Map topic ID to readable label
        label = topic_labels.get(topic_id, f"Topic {topic_id}")

        print(f"[DONE] {file.filename} → {label}")

        # Cleanup temp file
        os.remove(temp_path)

        return {
            "filename": file.filename,
            "topic_id": topic_id,
            "label": label
        }

    except Exception as e:
        return {"error": str(e)}
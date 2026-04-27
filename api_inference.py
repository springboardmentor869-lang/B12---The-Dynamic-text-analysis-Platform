"""
API endpoint for topic inference/classification.
POST /api/inference
"""

from fastapi import APIRouter, UploadFile, File
import os
import shutil
import json
from backend.convert_document import extract_with_fallback
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

router = APIRouter()

# ───────────────────────────────────────────────
# LOAD MODEL (FIXED PATH VERSION)
# ───────────────────────────────────────────────
try:
    print("\n=== LOADING TOPIC MODEL ===")

    # Base directory (project root)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Paths
    MODEL_PATH = os.path.join(BASE_DIR, "backend", "models", "bertopic_model")
    LABELS_PATH = os.path.join(BASE_DIR, "backend", "models", "topic_labels.json")
    KEYWORDS_PATH = os.path.join(BASE_DIR, "backend", "models", "topic_keywords.json")

    print("MODEL PATH:", MODEL_PATH)

    # Load embedding model
    print("Loading embedding model...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    # Load BERTopic model
    print("Loading BERTopic model...")
    topic_model = BERTopic.load(MODEL_PATH, embedding_model=embedding_model)

    # Load labels
    print("Loading labels...")
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        topic_labels = json.load(f)

    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        topic_keywords = json.load(f)

    print("✅ MODEL LOADED SUCCESSFULLY\n")

except Exception as e:
    import traceback
    print("❌ MODEL LOADING FAILED")
    traceback.print_exc()

    topic_model = None
    topic_labels = {}
    topic_keywords = {}

# ───────────────────────────────────────────────
# API ENDPOINT
# ───────────────────────────────────────────────
@router.post("/inference")
async def infer_topics(file: UploadFile = File(...)):
    """Classify document into topic."""

    if topic_model is None:
        return {"status": "error", "error": "Topic model not loaded"}

    temp_path = f"temp_{file.filename}"

    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text
        text = extract_with_fallback(temp_path)

        if not text.strip():
            return {"status": "error", "error": "Could not extract text"}

        # Run inference
        topics, probs = topic_model.transform([text])
        topic_id = str(topics[0])

        # Handle outlier
        if topic_id == "-1":
            return {
                "status": "success",
                "filename": file.filename,
                "topic_id": -1,
                "topic_label": "Unclassified",
                "keywords": [],
                "confidence": 0.0
            }

        # Get label + keywords
        topic_label = topic_labels.get(topic_id, f"Topic {topic_id}")
        keywords = topic_keywords.get(topic_id, [])

        # Confidence
        confidence = float(probs[0][int(topic_id)])

        return {
            "status": "success",
            "filename": file.filename,
            "topic_id": int(topic_id),
            "topic_label": topic_label,
            "confidence": confidence
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
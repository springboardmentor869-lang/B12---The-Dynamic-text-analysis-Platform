import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

STORAGE_DIR = os.path.join(BASE_DIR, "storage")

UPLOAD_DIR = os.path.join(STORAGE_DIR, "uploads")
OUTPUT_DIR = os.path.join(STORAGE_DIR, "outputs")
MODEL_DIR = os.path.join(STORAGE_DIR, "models")

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
OLLAMA_URL = "http://localhost:11434/api/generate"
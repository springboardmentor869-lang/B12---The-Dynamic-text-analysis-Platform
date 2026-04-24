import torch
from sentence_transformers import SentenceTransformer

_embedding_model = None

def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading SentenceTransformer on device: {device}")
        _embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            device=device
        )

    return _embedding_model
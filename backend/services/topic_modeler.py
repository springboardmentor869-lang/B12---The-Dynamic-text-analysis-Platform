import json
import os
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer
from core.config import settings


class TopicModeler:
    """BERTopic-based topic modeling service."""

    _instance: Optional["TopicModeler"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.centroids: dict = {}
        self.topic_labels: dict = {}
        self.embedding_model: Optional[SentenceTransformer] = None
        self.load_error: Optional[Exception] = None
        try:
            self._load_artifacts()
        except Exception as e:
            # Keep the API bootable even if artifacts are missing; endpoints will
            # return a clear error when topic classification is requested.
            self.load_error = e
        self._initialized = True

    def _load_artifacts(self):
        """Load pre-trained topic model artifacts."""
        model_dir = settings.bertopic_model_dir

        if not model_dir.exists():
            raise FileNotFoundError(
                f"Topic model not found at {model_dir}. "
                "Please train the model first using train_bertopic.py"
            )

        # Load centroids
        centroids_path = model_dir / "centroids.pkl"
        with open(centroids_path, "rb") as f:
            self.centroids = pickle.load(f)

        # Load topic labels
        labels_path = model_dir / "topic_labels.json"
        with open(labels_path, "r") as f:
            self.topic_labels = json.load(f)

        # Load embedding model
        self.embedding_model = SentenceTransformer(settings.embedding_model_name)

    def _split_into_chunks(self, text: str, chunk_size: int = 500) -> list[str]:
        """Split document into chunks of ~chunk_size words."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    def _classify_chunk(self, chunk_embedding: np.ndarray) -> dict:
        """Classify a chunk against topic centroids."""
        best_topic_id = None
        best_score = -1
        best_label = "Out of Domain"
        best_keywords = []

        for topic_id, data in self.centroids.items():
            score = self._cosine_similarity(chunk_embedding, data["centroid"])
            if score > best_score:
                best_score = score
                best_topic_id = topic_id
                best_label = data["label"]
                best_keywords = data.get("keywords", [])

        threshold = settings.similarity_threshold
        if best_score < threshold:
            return {
                "topic_id": -1,
                "label": "Out of Domain",
                "score": round(best_score, 4),
                "keywords": [],
            }

        return {
            "topic_id": int(best_topic_id),
            "label": best_label,
            "score": round(best_score, 4),
            "keywords": best_keywords,
        }

    def classify_document(self, markdown_content: str, chunk_size: int = 500) -> dict:
        """
        Classify document into topics.

        Returns dict with dominant_topic, all_topics_found, and chunk_details.
        """
        if self.embedding_model is None or not self.centroids:
            if self.load_error:
                raise FileNotFoundError(str(self.load_error))
            raise FileNotFoundError(
                f"Topic model not found at {settings.bertopic_model_dir}. "
                "Please train the model first using train_bertopic.py"
            )

        chunks = self._split_into_chunks(markdown_content, chunk_size=chunk_size)

        # Embed chunks
        embeddings = self.embedding_model.encode(chunks, show_progress_bar=False)

        # Classify each chunk
        chunk_results = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            result = self._classify_chunk(embedding)
            chunk_results.append({
                "chunk_id": i + 1,
                "preview": " ".join(chunk.split()[:20]) + "...",
                **result,
            })

        # Aggregate results by topic
        topic_counts = {}
        for res in chunk_results:
            if res["topic_id"] != -1:
                tid = res["topic_id"]
                label = res["label"]
                if tid not in topic_counts:
                    topic_counts[tid] = {"count": 0, "label": label, "scores": []}
                topic_counts[tid]["count"] += 1
                topic_counts[tid]["scores"].append(res["score"])

        # Find dominant topic
        if topic_counts:
            dominant_topic_id = max(topic_counts, key=lambda x: topic_counts[x]["count"])
            dominant_label = topic_counts[dominant_topic_id]["label"]
            avg_score = round(np.mean(topic_counts[dominant_topic_id]["scores"]), 4)
        else:
            dominant_topic_id = -1
            dominant_label = "Out of Domain"
            avg_score = 0.0

        return {
            "dominant_topic": {
                "topic_id": int(dominant_topic_id),
                "label": dominant_label,
                "avg_similarity_score": avg_score,
                "chunks_matched": topic_counts.get(dominant_topic_id, {}).get("count", 0),
                "total_chunks": len(chunks),
            },
            "all_topics_found": [
                {
                    "topic_id": int(tid),
                    "label": data["label"],
                    "chunks_matched": data["count"],
                    "avg_score": round(np.mean(data["scores"]), 4),
                }
                for tid, data in sorted(
                    topic_counts.items(), key=lambda x: x[1]["count"], reverse=True
                )
            ],
            "chunk_details": chunk_results,
        }


# Singleton instance
topic_modeler = TopicModeler()

import nltk
from collections import Counter
from typing import Optional

import torch
from transformers import pipeline

nltk.download("punkt_tab", quiet=True)

MODEL_NAME = "ProsusAI/finbert"
MAX_TOKENS = 500


class SentimentAnalyzer:
    """FinBERT-based sentiment analysis service."""

    _instance: Optional["SentimentAnalyzer"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.pipeline = pipeline(
            "sentiment-analysis", model=MODEL_NAME, tokenizer=MODEL_NAME
        )
        self._initialized = True

    def _chunk_text(self, text: str, max_tokens: int = MAX_TOKENS) -> list[str]:
        """Split text into chunks that fit within token limit."""
        tokens = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for token in tokens:
            token_len = len(token)
            if current_length + token_len + 1 > max_tokens:
                chunks.append(" ".join(current_chunk))
                current_chunk = [token]
                current_length = token_len
            else:
                current_chunk.append(token)
                current_length += token_len + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _get_token_count(self, text: str) -> int:
        """Get token count for text."""
        tokens = self.pipeline.tokenizer.encode(text, add_special_tokens=True)
        return len(tokens)

    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of text.

        Returns dict with overall_sentiment, summary, and per_sentence.
        """
        sentences = nltk.sent_tokenize(text)
        results = []

        for sentence in sentences:
            token_count = self._get_token_count(sentence)

            if token_count > MAX_TOKENS:
                # Chunk the sentence and analyze each part
                chunks = self._chunk_text(sentence, MAX_TOKENS)
                chunk_results = []
                for chunk in chunks:
                    result = self.pipeline(chunk)[0]
                    chunk_results.append({
                        "label": result["label"],
                        "score": float(result["score"]),
                    })

                # Aggregate chunk results
                label_scores = {}
                for cr in chunk_results:
                    label = cr["label"]
                    if label not in label_scores:
                        label_scores[label] = []
                    label_scores[label].append(cr["score"])

                avg_scores = {
                    label: sum(scores) / len(scores)
                    for label, scores in label_scores.items()
                }
                best_label = max(avg_scores, key=avg_scores.get)
                best_score = avg_scores[best_label]

                results.append({
                    "sentence": sentence[:200] + "..." if len(sentence) > 200 else sentence,
                    "label": best_label,
                    "score": best_score,
                    "chunked": True,
                })
            else:
                result = self.pipeline(sentence)[0]
                results.append({
                    "sentence": sentence,
                    "label": result["label"],
                    "score": float(result["score"]),
                    "chunked": False,
                })

        # Calculate overall sentiment
        labels = [r["label"] for r in results]
        label_counts = Counter(labels)

        if label_counts:
            overall = label_counts.most_common(1)[0][0]
        else:
            overall = "neutral"

        # Calculate summary percentages
        total = len(results)
        summary = {
            "positive": round(label_counts.get("positive", 0) / total, 2) if total > 0 else 0.0,
            "negative": round(label_counts.get("negative", 0) / total, 2) if total > 0 else 0.0,
            "neutral": round(label_counts.get("neutral", 0) / total, 2) if total > 0 else 0.0,
        }

        return {
            "overall_sentiment": overall,
            "summary": summary,
            "per_sentence": results,
        }


# Singleton instance
sentiment_analyzer = SentimentAnalyzer()

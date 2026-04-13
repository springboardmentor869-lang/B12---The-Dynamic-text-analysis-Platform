import os
import sys
import nltk
from collections import Counter
from typing import Optional
from pathlib import Path

# --- SILENCE WARNINGS ---
import warnings
warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import transformers
transformers.logging.set_verbosity_error() 

import torch
from transformers import pipeline

nltk.download("punkt_tab", quiet=True)

# 🧠 PHASE 2 CHANGE: Swapping from FinBERT to General Purpose RoBERTa
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
MAX_TOKENS = 400 

class SentimentAnalyzer:
    """General-purpose RoBERTa-based sentiment analysis service."""

    _instance: Optional["SentimentAnalyzer"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        print(f"🧠 Loading {MODEL_NAME} (General Purpose) into memory...")
        self.pipeline = pipeline(
            "sentiment-analysis", model=MODEL_NAME, tokenizer=MODEL_NAME
        )
        
        # 🛠️ LABEL MAPPING: RoBERTa uses Label IDs. We map them back to standard names.
        # label_0 = negative, label_1 = neutral, label_2 = positive
        self.label_map = {
            "label_0": "negative",
            "label_1": "neutral",
            "label_2": "positive"
        }
        
        self._initialized = True

    def _chunk_text(self, text: str, max_tokens: int = MAX_TOKENS) -> list[str]:
        """Split text into chunks based on character approximation (1 token ≈ 4 chars)."""
        max_chars = max_tokens * 4
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > max_chars:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _get_token_count(self, text: str) -> int:
        """Get token count safely using the Transformer tokenizer."""
        tokens = self.pipeline.tokenizer.encode(text, add_special_tokens=True)
        return len(tokens)

    def analyze(self, text: str) -> dict:
        """Analyze sentiment of text using contextual Transformer logic."""
        
        # 1. Text Segmentation (Paragraphs -> Sentences)
        raw_blocks = [block.strip() for block in text.split('\n\n') if block.strip()]
        sentences = []
        for block in raw_blocks:
            sentences.extend(nltk.sent_tokenize(block))
            
        # Filter out tiny garbage strings
        sentences = [s for s in sentences if len(s) > 20]
        
        results = []
        print(f"🔍 Analyzing {len(sentences)} blocks with {MODEL_NAME}...")

        for i, sentence in enumerate(sentences):
            if i > 0 and i % 10 == 0:
                print(f"   ...processed {i}/{len(sentences)} items")
                
            token_count = self._get_token_count(sentence)

            # Handle sentences that exceed the model's context window (512 tokens)
            if token_count > MAX_TOKENS:
                chunks = self._chunk_text(sentence, MAX_TOKENS)
                chunk_results = []
                for chunk in chunks:
                    res = self.pipeline(chunk, truncation=True, max_length=512)[0]
                    # Map 'label_X' to 'positive/negative/neutral'
                    mapped_label = self.label_map.get(res["label"].lower(), "neutral")
                    chunk_results.append({
                        "label": mapped_label,
                        "score": float(res["score"]),
                    })

                label_scores = {}
                for cr in chunk_results:
                    label = cr["label"]
                    if label not in label_scores:
                        label_scores[label] = []
                    label_scores[label].append(cr["score"])

                avg_scores = {l: sum(s) / len(s) for l, s in label_scores.items()}
                best_label = max(avg_scores, key=avg_scores.get)
                best_score = avg_scores[best_label]

                results.append({
                    "sentence": sentence[:150] + "..." if len(sentence) > 150 else sentence,
                    "label": best_label,
                    "score": best_score,
                    "chunked": True,
                })
            else:
                res = self.pipeline(sentence, truncation=True, max_length=512)[0]
                mapped_label = self.label_map.get(res["label"].lower(), "neutral")
                results.append({
                    "sentence": sentence[:150] + "..." if len(sentence) > 150 else sentence,
                    "label": mapped_label,
                    "score": float(res["score"]),
                    "chunked": False,
                })

        # --- AGGREGATION ---
        labels = [r["label"] for r in results]
        label_counts = Counter(labels)
        overall = label_counts.most_common(1)[0][0] if label_counts else "neutral"

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

if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent 
    
    # Locate document for testing
    target_file = str(project_root / "processed_data" / "financial_doc.md")
    
    if not os.path.exists(target_file):
        print(f"❌ CRITICAL: Could not find {target_file}")
        sys.exit(1)

    with open(target_file, "r", encoding="utf-8") as f:
        full_text = f.read()
        
    analyzer = SentimentAnalyzer()
    results = analyzer.analyze(full_text)
    
    # Generate Output Report
    report = f"""
==================================================
 📊 DYNAMIC REPORT: {results['overall_sentiment'].upper()}
==================================================
 Positive:  {results['summary']['positive']:.0%}
 Negative:  {results['summary']['negative']:.0%}
 Neutral:   {results['summary']['neutral']:.0%}
--------------------------------------------------
 Top Sentences Analyzed:
"""
    for i, item in enumerate(results['per_sentence'][:10]):
        snippet = item['sentence'].replace('\n', ' ')
        report += f" {i+1}. [{item['label'].upper()}] - {snippet}\n"
        
    report += "==================================================\n"
    print(report)

    output_path = current_dir / "sentiment_roberta_report.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ General-Purpose Report saved to: {output_path}")
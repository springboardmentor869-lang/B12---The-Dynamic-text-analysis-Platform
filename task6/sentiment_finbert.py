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
transformers.logging.set_verbosity_error() # Shuts up the 512-token warning

import torch
from transformers import pipeline

nltk.download("punkt_tab", quiet=True)

MODEL_NAME = "ProsusAI/finbert"
MAX_TOKENS = 400 # Lowered slightly for a safer margin

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
            
        print(f"🧠 Loading {MODEL_NAME} into memory...")
        self.pipeline = pipeline(
            "sentiment-analysis", model=MODEL_NAME, tokenizer=MODEL_NAME
        )
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
        """Get token count safely."""
        # Using truncation=False triggers the warning, but we silenced it globally above!
        tokens = self.pipeline.tokenizer.encode(text, add_special_tokens=True)
        return len(tokens)

    def analyze(self, text: str) -> dict:
        """Analyze sentiment of text."""
        
        # --- SMARTER TEXT SPLITTING ---
        # 1. Split by double newlines (paragraphs/tables) first
        raw_blocks = [block.strip() for block in text.split('\n\n') if block.strip()]
        
        sentences = []
        # 2. Then split those blocks by sentences
        for block in raw_blocks:
            sentences.extend(nltk.sent_tokenize(block))
            
        # 3. Filter out tiny garbage strings (like a stray "*" or "---")
        sentences = [s for s in sentences if len(s) > 20]
        
        results = []
        
        print(f"🔍 Analyzing {len(sentences)} distinct blocks/sentences with FinBERT...")

        for i, sentence in enumerate(sentences):
            if i > 0 and i % 10 == 0:
                print(f"   ...processed {i}/{len(sentences)} items")
                
            token_count = self._get_token_count(sentence)

            if token_count > MAX_TOKENS:
                chunks = self._chunk_text(sentence, MAX_TOKENS)
                chunk_results = []
                for chunk in chunks:
                    # Truncate=True ensures absolute safety for the pipeline
                    result = self.pipeline(chunk, truncation=True, max_length=512)[0]
                    chunk_results.append({
                        "label": result["label"],
                        "score": float(result["score"]),
                    })

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
                    "sentence": sentence[:150] + "..." if len(sentence) > 150 else sentence,
                    "label": best_label,
                    "score": best_score,
                    "chunked": True,
                })
            else:
                result = self.pipeline(sentence, truncation=True, max_length=512)[0]
                results.append({
                    "sentence": sentence[:150] + "..." if len(sentence) > 150 else sentence,
                    "label": result["label"],
                    "score": float(result["score"]),
                    "chunked": False,
                })

        labels = [r["label"] for r in results]
        label_counts = Counter(labels)

        if label_counts:
            overall = label_counts.most_common(1)[0][0]
        else:
            overall = "neutral"

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
    
    possible_paths = [
        project_root / "processed_data" / "financial doc.md",
        project_root / "processed_data" / "financial_doc.md"
    ]
    
    target_file = None
    for p in possible_paths:
        if p.exists():
            target_file = str(p)
            break
            
    if not target_file:
        print(f"❌ CRITICAL: Could not find the file in {project_root / 'processed_data'}")
        sys.exit(1)

    print(f"\n📄 Loading document: {target_file}")
    with open(target_file, "r", encoding="utf-8") as f:
        full_text = f.read()
        
    # We slice to 10,000 characters for a fast terminal test.
    # Change this to full_text once you know it works!
# Let FinBERT read the entire document!
    analyzer = SentimentAnalyzer()
    results = analyzer.analyze(full_text)
    
    # --- NEW: Build the report as a single string ---
    report = f"""
==================================================
 📊 FINAL REPORT: {results['overall_sentiment'].upper()}
==================================================
 Positive:  {results['summary']['positive']:.0%}
 Negative:  {results['summary']['negative']:.0%}
 Neutral:   {results['summary']['neutral']:.0%}
--------------------------------------------------
 Top 3 Sentences Analyzed:
"""
    for i, item in enumerate(results['per_sentence'][:10]):
        snippet = item['sentence'].replace('\n', ' ')
        report += f" {i+1}. [{item['label'].upper()}] - {snippet}\n"
        
    report += "==================================================\n"

    # Print to the terminal so you can see it immediately
    print(report)

    # --- NEW: Save the report to a file ---
    output_path = current_dir / "sentiment_finbert_report.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"✅ Report successfully saved to: {output_path}")
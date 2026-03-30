import sys
from pathlib import Path
from typing import Dict
from services.extractor import chunk_text

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Load Task 7 Model safely
try:
    from task7.run_inference import FastTopicPredictor
    predictor = FastTopicPredictor()
except ImportError:
    predictor = None

# Load Task 6 (FinBERT)
try:
    from task6.sentiment_finbert import SentimentAnalyzer
    # Initialize the Singleton class once when the server starts!
    sentiment_analyzer = SentimentAnalyzer() 
    HAS_TASK6 = True
except ImportError as e:
    print(f"⚠️ Warning: Could not import task6 FinBERT: {e}")
    HAS_TASK6 = False

# Load Task 5
try:
    from task5.summarizer_openrouter import summarize_text
    HAS_TASK5 = True
except ImportError:
    HAS_TASK5 = False

def run_topic_pipeline(text: str) -> dict:
    if not predictor:
        return {"dominant_topic": {"topic_id": -1, "label": "Model Offline", "avg_similarity_score": 0.0, "chunks_matched": 0, "total_chunks": 0}, "all_topics_found": [], "chunk_details": []}

    chunks = chunk_text(text)
    chunk_details, topic_counts = [], {}
    
    for idx, chunk in enumerate(chunks):
        topic_id, label, confidence = predictor.predict(chunk)
        try:
            tid = int(float(topic_id)) if str(topic_id) != "Unknown" else -1
        except Exception:
            tid = -1
        
        chunk_details.append({"chunk_id": idx + 1, "preview": chunk[:100] + "...", "topic_id": tid, "label": label, "score": float(confidence), "keywords": []})
        if tid not in topic_counts: topic_counts[tid] = {"label": label, "scores": []}
        topic_counts[tid]["scores"].append(float(confidence))

    all_topics, best_topic_id, max_chunks = [], -1, 0
    for tid, data in topic_counts.items():
        avg_score = sum(data["scores"]) / len(data["scores"])
        chunks_matched = len(data["scores"])
        all_topics.append({"topic_id": tid, "label": data["label"], "chunks_matched": chunks_matched, "avg_score": avg_score})
        if chunks_matched > max_chunks:
            max_chunks = chunks_matched
            best_topic_id = tid

    if best_topic_id == -1 or max_chunks == 0:
        dominant = {"topic_id": -1, "label": "Uncategorized", "avg_similarity_score": 0.0, "chunks_matched": 0, "total_chunks": len(chunks)}
    else:
        dominant = {"topic_id": best_topic_id, "label": topic_counts[best_topic_id]["label"], "avg_similarity_score": sum(topic_counts[best_topic_id]["scores"]) / max_chunks, "chunks_matched": max_chunks, "total_chunks": len(chunks)}

    return {"dominant_topic": dominant, "all_topics_found": all_topics, "chunk_details": chunk_details}

def run_sentiment_pipeline(text: str) -> dict:
    if HAS_TASK6:
        # 🛡️ SHIELD: We don't need sentiment for all 48 pages.
        # The first 30,000 chars (about 10 pages) is enough to gauge the document's mood.
        # This keeps your API lightning fast!
        safe_text = text[:30000]
        
        # Call the FinBERT analyzer
        result = sentiment_analyzer.analyze(safe_text)
        
        return {
            "overall_sentiment": result["overall_sentiment"], 
            "per_sentence": result["per_sentence"],
            # You can also pass that awesome summary dictionary to your frontend!
            "summary": result["summary"] 
        }
        
    return {
        "overall_sentiment": "neutral", 
        "per_sentence": [], 
        "summary": {"positive": 0, "negative": 0, "neutral": 0}
    }

def run_summarize_pipeline(text: str) -> dict:
    if not HAS_TASK5:
        return {"summary": "Task 5 offline. Mock summary.", "word_count": 0}
        
    # 🛡️ SHIELD: Only send the first ~15,000 characters to OpenRouter.
    # This prevents the 402/429 errors from triggering!
    safe_text = text[:15000] 
    
    summary_text = summarize_text(safe_text)
    
    # Catch the error messages so the frontend doesn't crash
    if "Critical Error" in summary_text or "Unexpected Error" in summary_text:
        return {"summary": summary_text, "word_count": 0}
        
    return {"summary": summary_text, "word_count": len(summary_text.split())}
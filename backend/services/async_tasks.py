import time
from typing import Dict
from services.extractor import extract_text_smart
from services.pipelines import run_topic_pipeline, run_sentiment_pipeline, run_summarize_pipeline

tasks_db: Dict[str, dict] = {}

def process_full_document(task_id: str, file_bytes: bytes, filename: str):
    tasks_db[task_id]["status"] = "processing"
    start_time = time.time()
    try:
        full_text = extract_text_smart(file_bytes)
        if not full_text: raise ValueError("Could not extract text.")
            
        topic_results = run_topic_pipeline(full_text)
        sentiment_results = run_sentiment_pipeline(full_text)
        summary_results = run_summarize_pipeline(full_text)
        
        tasks_db[task_id]["results"] = {
            "file_name": filename,
            "topic_modeling": topic_results,
            "sentiment_analysis": sentiment_results,
            "summarization": summary_results,
            "processing_time_seconds": round(time.time() - start_time, 2)
        }
        tasks_db[task_id]["status"] = "completed"
    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)
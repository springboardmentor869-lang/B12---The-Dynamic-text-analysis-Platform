import sys
import os
import time
import uuid
import tempfile
import fitz
from pathlib import Path
from typing import List, Optional, Dict
from contextlib import contextmanager
from io import StringIO

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel

import nltk
from nltk.tokenize import sent_tokenize

# Ensure NLTK tokenizer is available for sentence splitting
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

# Context manager to suppress stdout
@contextmanager
def suppress_stdout():
    """Suppress print statements from external functions."""
    save_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        yield
    finally:
        sys.stdout = save_stdout

# ==========================================
# CROSS-TASK IMPORTS
# ==========================================
# Add the root directory to sys.path so we can import from task5, task6, task7
sys.path.append(str(Path(__file__).resolve().parent.parent))
try:
    from task3.doc_parser import convert_bytes_to_markdown
    HAS_TASK3 = True
except ImportError:
    print("Warning: Task 3 doc_parser not found. Falling back to inline Docling.")
    HAS_TASK3 = False
try:
    from task7.run_inference import FastTopicPredictor
    predictor = FastTopicPredictor()
except ImportError as e:
    print(f"CRITICAL: Could not load Task 7 Model: {e}")
    exit(1)

# Try to import Task 5 and 6 logic. If they fail, we will use mock logic 
# so the API doesn't crash the frontend while you are testing.
try:
    from task5.summarizer_openrouter import summarize_text
    HAS_TASK5 = True
except ImportError:
    print("Warning: Task 5 summarizer not found. Using fallback logic.")
    HAS_TASK5 = False

try:
    from task6.sentiment_analyzer import analyze_text_sentiment
    HAS_TASK6 = True
except ImportError:
    print("Warning: Task 6 sentiment analyzer not found. Using fallback logic.")
    HAS_TASK6 = False


app = FastAPI(title="Dynamic Text Analysis API")

# ==========================================
# PYDANTIC SCHEMAS (Matches React TypeScript)
# ==========================================

# Topic Schemas
class DominantTopic(BaseModel):
    topic_id: int
    label: str
    avg_similarity_score: float
    chunks_matched: int
    total_chunks: int

class TopicFound(BaseModel):
    topic_id: int
    label: str
    chunks_matched: int
    avg_score: float

class ChunkDetail(BaseModel):
    chunk_id: int
    preview: str
    topic_id: int
    label: str
    score: float
    keywords: List[str]

class TopicModelResponse(BaseModel):
    dominant_topic: DominantTopic
    all_topics_found: List[TopicFound]
    chunk_details: List[ChunkDetail]

# Sentiment Schemas
class SentenceSentiment(BaseModel):
    sentence: str
    label: str
    score: float
    chunked: Optional[bool] = False

class SentimentResponse(BaseModel):
    overall_sentiment: str
    per_sentence: List[SentenceSentiment]

# Summarize Schemas
class SummarizeResponse(BaseModel):
    summary: str
    word_count: int

# Async / Analyze Schemas
class AnalyzeSubmitResponse(BaseModel):
    task_id: str
    status: str
    message: str

class AnalysisResults(BaseModel):
    file_name: str
    topic_modeling: TopicModelResponse
    sentiment_analysis: SentimentResponse
    summarization: SummarizeResponse
    processing_time_seconds: float

class AnalyzeStatusResponse(BaseModel):
    task_id: str
    status: str
    results: Optional[AnalysisResults] = None
    error: Optional[str] = None


# State management for async tasks
tasks_db: Dict[str, dict] = {}


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def extract_text_with_docling(file_bytes: bytes) -> str:
    """Tries Docling first, falls back to PyMuPDF if memory crashes."""
    
    # Try Docling First (High Quality Markdown)
    if HAS_TASK3:
        try:
            print("Attempting Docling extraction...")
            return convert_bytes_to_markdown(file_bytes)
        except Exception as e:
            print(f"Docling failed (likely memory issue: {e}). Switching to PyMuPDF...")
    
    # Fallback to PyMuPDF (Low Memory Usage)
    print("Running PyMuPDF fallback extraction...")
    text = ""
    try:
        # Load bytes directly into PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text() + "\n\n"
        doc.close()
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Both parsers failed: {str(e)}")

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Splits markdown/text into logical paragraphs."""
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
    if not paragraphs:
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return paragraphs


# ==========================================
# CORE PROCESSING LOGIC
# ==========================================

def run_topic_pipeline(text: str) -> dict:
    chunks = chunk_text(text)
    chunk_details = []
    topic_counts: Dict[int, dict] = {}
    
    for idx, chunk in enumerate(chunks):
        topic_id, label, confidence = predictor.predict(chunk)
        try:
            tid = int(float(topic_id)) if str(topic_id) != "Unknown" else -1
        except (ValueError, TypeError):
            tid = -1
        
        chunk_details.append({
            "chunk_id": idx + 1,
            "preview": chunk[:100] + "...", 
            "topic_id": tid,
            "label": label,
            "score": float(confidence),
            "keywords": []
        })
        
        if tid not in topic_counts:
            topic_counts[tid] = {"label": label, "scores": []}
        topic_counts[tid]["scores"].append(float(confidence))

    all_topics = []
    best_topic_id = -1
    max_chunks = 0
    
    for tid, data in topic_counts.items():
        avg_score = sum(data["scores"]) / len(data["scores"])
        chunks_matched = len(data["scores"])
        
        all_topics.append({
            "topic_id": tid,
            "label": data["label"],
            "chunks_matched": chunks_matched,
            "avg_score": avg_score
        })
        
        if chunks_matched > max_chunks:
            max_chunks = chunks_matched
            best_topic_id = tid

    if best_topic_id == -1 or max_chunks == 0:
        dominant = {"topic_id": -1, "label": "Uncategorized", "avg_similarity_score": 0.0, "chunks_matched": 0, "total_chunks": len(chunks)}
    else:
        avg_sim = sum(topic_counts[best_topic_id]["scores"]) / len(topic_counts[best_topic_id]["scores"])
        dominant = {
            "topic_id": best_topic_id,
            "label": topic_counts[best_topic_id]["label"],
            "avg_similarity_score": avg_sim,
            "chunks_matched": max_chunks,
            "total_chunks": len(chunks)
        }

    return {
        "dominant_topic": dominant,
        "all_topics_found": all_topics,
        "chunk_details": chunk_details
    }

def run_sentiment_pipeline(text: str) -> dict:
    if HAS_TASK6:
        # Call the new function you just wrote!
        result = analyze_text_sentiment(text)
        
        # Format it exactly how the React frontend wants it
        return {
            "overall_sentiment": result["overall_sentiment"],
            "per_sentence": result["per_sentence"]
        }
    else:
        return {"overall_sentiment": "neutral", "per_sentence": []}

def run_summarize_pipeline(text: str) -> dict:
    if HAS_TASK5:
        # Call the new function you just wrote!
        summary_text = summarize_text(text) 
    else:
        summary_text = "Task 5 offline. Mock summary."
        
    word_count = len(summary_text.split())
    return {
        "summary": summary_text,
        "word_count": word_count
    }


# ==========================================
# ASYNC WORKER
# ==========================================

def process_full_document(task_id: str, file_bytes: bytes, filename: str):
    tasks_db[task_id]["status"] = "processing"
    start_time = time.time()
    
    try:
        full_text = extract_text_with_docling(file_bytes)
        if not full_text or full_text is None:
            raise ValueError("Could not extract text from document.")
            
        topic_results = run_topic_pipeline(full_text)
        sentiment_results = run_sentiment_pipeline(full_text)
        summary_results = run_summarize_pipeline(full_text)
        
        end_time = time.time()
        
        tasks_db[task_id]["results"] = {
            "file_name": filename,
            "topic_modeling": topic_results,
            "sentiment_analysis": sentiment_results,
            "summarization": summary_results,
            "processing_time_seconds": round(end_time - start_time, 2)
        }
        tasks_db[task_id]["status"] = "completed"

    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)


# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/")
async def root():
    return {"message": "Dynamic Text Analysis API is active. React frontend integration ready."}

@app.post("/topic-model", response_model=TopicModelResponse)
async def endpoint_topic_model(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'): raise HTTPException(status_code=400, detail="PDF only.")
    text = extract_text_with_docling(await file.read())
    return run_topic_pipeline(text)

@app.post("/sentiment", response_model=SentimentResponse)
async def endpoint_sentiment(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'): raise HTTPException(status_code=400, detail="PDF only.")
    text = extract_text_with_docling(await file.read())
    return run_sentiment_pipeline(text)

@app.post("/summarize", response_model=SummarizeResponse)
async def endpoint_summarize(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'): raise HTTPException(status_code=400, detail="PDF only.")
    text = extract_text_with_docling(await file.read())
    return run_summarize_pipeline(text)

@app.post("/analyze", response_model=AnalyzeSubmitResponse)
async def endpoint_analyze_submit(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'): raise HTTPException(status_code=400, detail="PDF only.")
    task_id = str(uuid.uuid4())
    file_bytes = await file.read()
    
    tasks_db[task_id] = {"status": "pending", "results": None, "error": None}
    background_tasks.add_task(process_full_document, task_id, file_bytes, file.filename)
    
    return {"task_id": task_id, "status": "pending", "message": "Document submitted."}

@app.get("/analyze/{task_id}", response_model=AnalyzeStatusResponse)
async def endpoint_analyze_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task_id,
        "status": tasks_db[task_id]["status"],
        "results": tasks_db[task_id].get("results"),
        "error": tasks_db[task_id].get("error")
    }
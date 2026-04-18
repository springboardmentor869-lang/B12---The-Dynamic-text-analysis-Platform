from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import json

from parsers.file_parser import extract_text_from_file
from converter.convert import DocumentParser
from preprocessing.preprocess import clean_text
from summarization.summarize import summarize_text
from sentiment_analysis import analyze_sentiment
from topic_training.topic_inference import classify_document

app = FastAPI()

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    os.makedirs("uploads", exist_ok=True)

# =====================================================
# MAIN ANALYZE ROUTE
# =====================================================

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    selected_tasks: str = Form(...)
):
    try:
        if not file.filename:
            return {"error": "Invalid file name"}

        # Sanitize filename to prevent path traversal
        safe_filename = os.path.basename(file.filename).replace(" ", "_")
        file_path = os.path.join("uploads", safe_filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        raw_text = extract_text_from_file(file_path)
        text = clean_text(raw_text)

        if not text:
            return {"error": "No text extracted from file"}

        try:
            tasks = json.loads(selected_tasks)
        except Exception:
            return {"error": "Invalid selected_tasks format"}

        markdown_path = ""
        markdown_text = ""
        summary = ""
        sentiment = {}
        topic_result = {}

        # ── Run all selected tasks IN PARALLEL ──
        def run_conversion():
            nonlocal markdown_path, markdown_text
            try:
                parser = DocumentParser()
                markdown_path = parser.parse_and_save(file_path)
                if markdown_path and os.path.exists(markdown_path):
                    with open(markdown_path, "r", encoding="utf-8") as f:
                        markdown_text = f.read()
            except Exception as e:
                print("Document Conversion Error:", e)

        def run_summarization():
            nonlocal summary
            try:
                summary = summarize_text(text)
            except Exception as e:
                print("Summarization Error:", e)
                summary = "Summary could not be generated."

        def run_sentiment():
            nonlocal sentiment
            try:
                sentiment = analyze_sentiment(text)
            except Exception as e:
                print("Sentiment Error:", e)

        def run_topic():
            nonlocal topic_result
            try:
                topic_result = classify_document(text)
            except Exception as e:
                print("Topic Modeling Error:", e)

        task_map = {
            "Document Conversion": run_conversion,
            "Text Summarization": run_summarization,
            "Sentiment Analysis": run_sentiment,
            "Topic Modeling": run_topic,
        }

        # Submit all selected tasks to thread pool
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for task_name in tasks:
                if task_name in task_map:
                    futures.append(executor.submit(task_map[task_name]))
            # Wait for all to complete
            for future in as_completed(futures):
                future.result()  # raises if any task threw

        return {
            "filename": safe_filename,
            "selected_tasks": tasks,
            "markdown_file": markdown_path,
            "markdown_text": markdown_text,
            "summary": summary,
            "sentiment": sentiment,
            "topic": topic_result
        }

    except Exception as e:
        print("APP ERROR:", e)
        return {"error": str(e)}
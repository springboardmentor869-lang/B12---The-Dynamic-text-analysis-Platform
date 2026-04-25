from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
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

# =====================================================
# MAIN ANALYZE ROUTE
# =====================================================

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    selected_tasks: str = Form(...)
):
    try:
        os.makedirs("uploads", exist_ok=True)

        if not file.filename:
            return {"error": "Invalid file name"}

        file_path = os.path.join("uploads", file.filename)

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

        if "Document Conversion" in tasks:
            try:
                parser = DocumentParser()
                markdown_path = parser.parse_and_save(file_path)

                if markdown_path and os.path.exists(markdown_path):
                    with open(markdown_path, "r", encoding="utf-8") as f:
                        markdown_text = f.read()

            except Exception as e:
                print("Document Conversion Error:", e)
                markdown_path = ""
                markdown_text = ""

        if "Text Summarization" in tasks:
            try:
                summary = summarize_text(text)
            except Exception as e:
                print("Summarization Error:", e)
                summary = "Summary could not be generated."

        if "Sentiment Analysis" in tasks:
            try:
                sentiment = analyze_sentiment(text)
            except Exception as e:
                print("Sentiment Error:", e)
                sentiment = {}

        if "Topic Modeling" in tasks:
            try:
                topic_result = classify_document(text)
            except Exception as e:
                print("Topic Modeling Error:", e)
                topic_result = {}

        return {
            "filename": file.filename,
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
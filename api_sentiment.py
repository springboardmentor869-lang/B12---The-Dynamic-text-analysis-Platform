"""
api_sentiment.py - FastAPI endpoint for document sentiment analysis.

Provides:
- REST API endpoint to upload documents (TXT, PDF, DOCX)
- Extract text using parsers (docx / pymupdf / OCR fallback)
- Perform sentence-level and document-level sentiment analysis
- Return structured sentiment results

Endpoint:
- POST /sentiment-file

Pipeline:
1. Receive uploaded file
2. Save file temporarily
3. Extract text based on file type
4. Fallback to OCR for scanned PDFs
5. Perform sentiment analysis using analyze_document()
6. Return sentiment results as JSON

Requires:
- fastapi               - API framework
- shutil                - file handling
- os                    - filesystem operations
- sentiment_analysis.py - core sentiment logic
- parsers.py            - document parsing utilities

Supported File Types:
- .txt  - direct read
- .pdf  - pymupdf (with OCR fallback)
- .docx - python-docx parser

Input:
- Multipart file upload (.txt, .pdf, .docx)

Output:
- JSON response:
    {
        "filename": "...",
        "result": {
            "sentence_results": [...],
            "counts": {...},
            "overall_sentiment": "..."
        }
    }

Run:
    uvicorn api:app --reload
"""

from fastapi import APIRouter, UploadFile, File
import os
import shutil

from sentiment_analysis import analyze_document
from parsers import PARSERS

router = APIRouter()

# Paths
EXTRACTED_DIR = "results/extracted"
SENTIMENT_DIR = "results/sentiment"

os.makedirs(SENTIMENT_DIR, exist_ok=True)


# API Endpoint
@router.post("/sentiment-file")
async def analyze_sentiment_file(file: UploadFile = File(...)):

    temp_path = f"temp_{file.filename}"

    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = ""

        # Extract text based on file type
        if file.filename.lower().endswith(".txt"):
            with open(temp_path, "r", encoding="utf-8") as f:
                text = f.read()

        elif file.filename.lower().endswith(".pdf"):
            text = PARSERS["pymupdf"](temp_path)
            if not text.strip():
                print(f"[OCR FALLBACK] {file.filename}")
                text = PARSERS["ocr"](temp_path)

        elif file.filename.lower().endswith(".docx"):
            text = PARSERS["docx"](temp_path)

        else:
            return {"error": "Unsupported file type"}

        if not text.strip():
            return {"error": "Could not extract text from file"}

        # Run sentiment analysis
        result = analyze_document(text)

        print(f"[DONE] {file.filename}")

        return {
            "filename": file.filename,
            "result": result
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
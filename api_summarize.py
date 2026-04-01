"""
api_summarizer.py - FastAPI endpoint for document summarization.

Provides:
- REST API endpoint to upload documents (TXT, PDF, DOCX)
- Extract text using parsers (docx / pymupdf / OCR fallback)
- Generate summaries using Hugging Face summarization pipeline
- Save summaries to disk and return them in API response

Endpoint:
- POST /summarize-file

Pipeline:
1. Receive uploaded file
2. Save file temporarily
3. Extract text based on file type
4. Fallback to OCR for scanned PDFs
5. Generate summary using summarize_text()
6. Save summary to output directory
7. Return summary as JSON response

Requires:
- fastapi           - API framework
- shutil            - file handling
- os                - filesystem operations
- hf_summarizer.py  - Hugging Face summarization logic
- parsers.py        - document parsing utilities

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
        "summary": "...",
        "output_file": "..."
    }

- Saved file:
    results/summaries_hf/*_summary.txt

Run:
    uvicorn api:app --reload
"""

from fastapi import APIRouter, UploadFile, File
import os
import shutil

from hf_summarizer import summarize_text
from parsers import PARSERS

router = APIRouter()

# Paths
INPUT_DIR = "results/preprocessed"
OUTPUT_DIR = "results/summaries_hf"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# API Endpoint
@router.post("/summarize-file")
async def summarize_file(file: UploadFile = File(...)):

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

        # Check empty text
        if not text.strip():
            return {"error": "Could not extract text"}

        print(f"[PROCESSING] {file.filename}")

        # Generate summary
        summary = summarize_text(text)

        # Save output 
        output_name = file.filename.replace(".txt", "_summary.txt") \
                                   .replace(".pdf", "_summary.txt") \
                                   .replace(".docx", "_summary.txt")

        output_path = os.path.join(OUTPUT_DIR, output_name)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"[DONE] {file.filename}")

        return {
            "filename": file.filename,
            "summary": summary,
            "output_file": output_path
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
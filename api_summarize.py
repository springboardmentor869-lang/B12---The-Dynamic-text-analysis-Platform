"""
API endpoint for document summarization.
POST /api/summarize-file
"""

from fastapi import APIRouter, UploadFile, File
import os
import shutil
from backend.convert_document import extract_with_fallback
from backend.hf_summarizer import summarize_text

router = APIRouter()

OUTPUT_DIR = "results/summaries"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@router.post("/summarize-file")

async def summarize_file(file: UploadFile = File(...)):
    """Summarize uploaded document."""
    
    temp_path = f"temp_{file.filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = extract_with_fallback(temp_path)
        
        if not text.strip():
            return {"error": "Could not extract text"}
        
        summary = summarize_text(text)
        
        return {
            "status": "success",
            "filename": file.filename,
            "summary": summary
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
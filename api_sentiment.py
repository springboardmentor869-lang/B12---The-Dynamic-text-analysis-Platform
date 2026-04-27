"""
API endpoint for sentiment analysis.
POST /api/sentiment-file
"""

from fastapi import APIRouter, UploadFile, File
import os
import shutil
from backend.convert_document import extract_with_fallback
from backend.sentiment_analysis import analyze_document

router = APIRouter()

OUTPUT_DIR = "results/sentiments"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@router.post("/sentiment-file")

async def sentiment_analysis(file: UploadFile = File(...)):
    """Analyze sentiment of uploaded document."""
    
    temp_path = f"temp_{file.filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = extract_with_fallback(temp_path)
        
        if not text.strip():
            return {"error": "Could not extract text"}
        
        # Analyze sentiment
        #sentiments = analyze_document(text)
        results, counts, overall_sentiment = analyze_document(text)
        
        return {
            "status": "success",
            "filename": file.filename,
            #"sentiments": sentiments
            "sentiments": {
                "positive_count":    counts["positive"],
                "negative_count":    counts["negative"],
                "neutral_count":     counts["neutral"],
                "overall_sentiment": overall_sentiment,
    }
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
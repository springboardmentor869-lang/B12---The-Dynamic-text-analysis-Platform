from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import SentimentResponse
from services.extractor import extract_text_smart
from services.pipelines import run_sentiment_pipeline

router = APIRouter()

@router.post("/sentiment", response_model=SentimentResponse, tags=["Analysis"])
async def endpoint_sentiment(file: UploadFile = File(...)):
    ALLOWED_EXTS = ('.pdf', '.docx', '.pptx', '.html', '.xml', '.txt', '.md')
    if not file.filename.lower().endswith(ALLOWED_EXTS):
        raise HTTPException(status_code=400, detail="Unsupported file format.")

    text = extract_text_smart(await file.read())
    return run_sentiment_pipeline(text)
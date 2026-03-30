from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import TopicModelResponse
from services.extractor import extract_text_smart
from services.pipelines import run_topic_pipeline

router = APIRouter()

@router.post("/topic-model", response_model=TopicModelResponse, tags=["Analysis"])
async def endpoint_topic_model(file: UploadFile = File(...)):
    ALLOWED_EXTS = ('.pdf', '.docx', '.pptx', '.html', '.xml', '.txt', '.md')
    if not file.filename.lower().endswith(ALLOWED_EXTS):
        raise HTTPException(status_code=400, detail="Unsupported file format.")
    text = extract_text_smart(await file.read())
    return run_topic_pipeline(text)
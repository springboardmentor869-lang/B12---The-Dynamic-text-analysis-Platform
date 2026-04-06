from fastapi import APIRouter, File, HTTPException, UploadFile

from core.config import settings
from models.schemas import TopicModelResponse
from services.pdf_parser import parse_pdf_to_markdown, cleanup_temp_files
from services.topic_modeler import topic_modeler


router = APIRouter(prefix="/topic-model", tags=["topic-model"])


def validate_pdf(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")


@router.post("", response_model=TopicModelResponse)
async def analyze_topics(file: UploadFile = File(...)):
    """
    Perform topic modeling on a PDF.

    Returns dominant topic, all topics found, and chunk-level details.
    """
    validate_pdf(file)

    # Read and save PDF
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {settings.max_upload_size_mb}MB",
        )

    import uuid

    unique_id = uuid.uuid4().hex
    pdf_path = settings.upload_dir / f"{unique_id}.pdf"
    md_path = None

    try:
        with open(pdf_path, "wb") as f:
            f.write(contents)

        # Parse PDF
        markdown_content, md_path = parse_pdf_to_markdown(str(pdf_path))

        # Run topic modeling
        result = topic_modeler.classify_document(markdown_content)

        return TopicModelResponse(**result)

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Topic model not available: {str(e)}. Train the model first.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cleanup_temp_files(md_file_path=md_path, pdf_file_path=str(pdf_path))

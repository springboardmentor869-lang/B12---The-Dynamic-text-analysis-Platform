from fastapi import APIRouter, File, HTTPException, UploadFile

from core.config import settings
from models.schemas import SummarizeResponse
from services.pdf_parser import parse_pdf_to_markdown, cleanup_temp_files
from services.summarizer import get_summarizer


router = APIRouter(prefix="/summarize", tags=["summarize"])


def validate_pdf(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")


@router.post("", response_model=SummarizeResponse)
async def summarize_pdf(file: UploadFile = File(...)):
    """
    Summarize a PDF document.

    Returns the summary and word count.
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

        # Run summarization
        summarizer = get_summarizer()
        result = summarizer.summarize(markdown_content)

        return SummarizeResponse(
            summary=result["summary"],
            word_count=result["word_count"],
        )

    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cleanup_temp_files(md_file_path=md_path, pdf_file_path=str(pdf_path))

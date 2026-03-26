import time
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, BackgroundTasks

from core.config import settings
from core.task_store import task_store, TaskStatus
from models.schemas import (
    AnalyzeSubmitResponse,
    AnalyzeStatusResponse,
    TopicModelingResult,
    SentimentResult,
    SummarizationResult,
)
from services.pdf_parser import parse_pdf_to_markdown, cleanup_temp_files
from services.topic_modeler import topic_modeler
from services.sentiment import sentiment_analyzer
from services.summarizer import get_summarizer


router = APIRouter(prefix="/analyze", tags=["analyze"])


def validate_pdf(file: UploadFile) -> None:
    """Validate that uploaded file is a PDF."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")


def process_analysis(task_id: str, pdf_path: str, file_name: str) -> None:
    """Background task to process PDF analysis."""
    start_time = time.time()
    md_path = None

    try:
        task_store.update_task(task_id, TaskStatus.PROCESSING)

        # Parse PDF to Markdown
        markdown_content, md_path = parse_pdf_to_markdown(pdf_path)

        # Run topic modeling
        topic_result = topic_modeler.classify_document(markdown_content)

        # Run sentiment analysis
        sentiment_result = sentiment_analyzer.analyze(markdown_content)

        # Run summarization
        summarizer = get_summarizer()
        summary_result = summarizer.summarize(markdown_content)

        processing_time = time.time() - start_time

        results = {
            "file_name": file_name,
            "topic_modeling": topic_result,
            "sentiment_analysis": sentiment_result,
            "summarization": summary_result,
            "processing_time_seconds": round(processing_time, 2),
        }

        task_store.update_task(task_id, TaskStatus.COMPLETED, results=results)

    except FileNotFoundError as e:
        task_store.update_task(
            task_id, TaskStatus.FAILED, error=f"Model not found: {str(e)}"
        )
    except Exception as e:
        task_store.update_task(task_id, TaskStatus.FAILED, error=str(e))
    finally:
        cleanup_temp_files(md_file_path=md_path, pdf_file_path=pdf_path)


@router.post("", response_model=AnalyzeSubmitResponse, status_code=202)
async def submit_analysis(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Upload a PDF for analysis. Returns task_id for polling.

    Use GET /analyze/{task_id} to poll for results.
    """
    validate_pdf(file)

    # Check file size
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {settings.max_upload_size_mb}MB",
        )

    # Save PDF temporarily
    import uuid

    unique_id = uuid.uuid4().hex
    pdf_path = settings.upload_dir / f"{unique_id}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(contents)

    # Create task
    task = task_store.create_task(file.filename or "unknown.pdf")

    # Queue background processing
    background_tasks.add_task(
        process_analysis, task.task_id, str(pdf_path), file.filename or "unknown.pdf"
    )

    return AnalyzeSubmitResponse(
        task_id=task.task_id,
        status="processing",
        message="PDF uploaded successfully. Use task_id to poll for results.",
    )


@router.get("/{task_id}", response_model=AnalyzeStatusResponse)
async def get_analysis_status(task_id: str):
    """
    Poll for analysis results using task_id from POST /analyze.

    Returns:
    - status: "pending", "processing", "completed", or "failed"
    - results: populated when status is "completed"
    - error: populated when status is "failed"
    """
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    response = AnalyzeStatusResponse(
        task_id=task.task_id,
        status=task.status.value,
    )

    if task.status == TaskStatus.COMPLETED and task.results:
        response.results = task.results
        response.processing_time_seconds = task.results.get("processing_time_seconds")

    if task.status == TaskStatus.FAILED:
        response.error = task.error

    return response

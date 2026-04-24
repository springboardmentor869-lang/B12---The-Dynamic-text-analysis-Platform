from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Form
import asyncio

from core.pipeline import run_pipeline
from core.task_manager import TaskManager

router = APIRouter(prefix="/analysis", tags=["Analysis"])

task_manager = TaskManager()


@router.post("/")
async def analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form("summary")
):
    """
    Upload file and select analysis type:
    summary | sentiment | topics | full
    """

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="File is required")

    # Validate mode
    valid_modes = ["summary", "sentiment", "topics", "full"]
    if mode not in valid_modes:
        raise HTTPException(status_code=400, detail="Invalid mode")

    # Create task
    task_id = task_manager.create_task()

    content = await file.read()
    filename = file.filename

    # Wrapper to properly run async pipeline in background
    def run_task():
        asyncio.run(run_pipeline(content, filename, mode, task_id, task_manager))

    # Run in background
    background_tasks.add_task(run_task)

    return {
        "message": "Processing started",
        "task_id": task_id
    }


@router.get("/status/{task_id}")
def get_status(task_id: str):
    status = task_manager.get_status(task_id)

    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Task not found")

    return status


@router.get("/result/{task_id}")
def get_result(task_id: str):
    result = task_manager.get_result(task_id)

    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    return result
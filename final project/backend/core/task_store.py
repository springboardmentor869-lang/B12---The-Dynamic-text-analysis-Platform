import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisTask(BaseModel):
    task_id: str
    status: TaskStatus
    file_name: str
    error: Optional[str] = None
    results: Optional[dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class TaskStore:
    """In-memory store for analysis tasks."""

    def __init__(self):
        self._tasks: dict[str, AnalysisTask] = {}

    def create_task(self, file_name: str) -> AnalysisTask:
        task_id = str(uuid.uuid4())
        task = AnalysisTask(
            task_id=task_id,
            status=TaskStatus.PENDING,
            file_name=file_name,
            created_at=datetime.now(),
        )
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[AnalysisTask]:
        return self._tasks.get(task_id)

    def update_task(
        self,
        task_id: str,
        status: TaskStatus,
        results: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Optional[AnalysisTask]:
        task = self._tasks.get(task_id)
        if task:
            task.status = status
            if results is not None:
                task.results = results
            if error is not None:
                task.error = error
            if status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                task.completed_at = datetime.now()
            return task
        return None


task_store = TaskStore()

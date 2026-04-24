import uuid

class TaskManager:
    def __init__(self):
        self.tasks = {}

    def create_task(self):
        task_id = str(uuid.uuid4())

        self.tasks[task_id] = {
            "status": "processing",
            "progress_msg": "Initializing task...",
            "progress_pct": 0,
            "result": None
        }

        return task_id

    def update_progress(self, task_id, progress_msg, progress_pct=None):
        if task_id in self.tasks:
            self.tasks[task_id]["progress_msg"] = progress_msg
            if progress_pct is not None:
                self.tasks[task_id]["progress_pct"] = progress_pct

    def update_task(self, task_id, result):
        self.tasks[task_id]["status"] = "completed"
        self.tasks[task_id]["progress_msg"] = "Complete"
        self.tasks[task_id]["progress_pct"] = 100
        self.tasks[task_id]["result"] = result

    def fail_task(self, task_id, error):
        self.tasks[task_id]["status"] = "error"
        self.tasks[task_id]["progress_msg"] = f"Failed: {error}"
        self.tasks[task_id]["error"] = error

    def get_status(self, task_id):
        return self.tasks.get(task_id, {"status": "not_found"})

    def get_result(self, task_id):
        return self.tasks.get(task_id, {})
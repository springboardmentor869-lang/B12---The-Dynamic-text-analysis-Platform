import requests

BASE_URL = "http://127.0.0.1:8000/api"


def send_file(file, mode):
    """
    Upload file to backend and start processing.
    Returns task_id.
    """

    files = {"file": file}
    data = {"mode": mode}

    res = requests.post(f"{BASE_URL}/analysis/", files=files, data=data)

    # Debug (helpful during development)
    # print(res.status_code)
    # print(res.text)

    if res.status_code != 200:
        raise Exception(f"Upload failed: {res.text}")

    response_data = res.json()

    if "task_id" not in response_data:
        raise Exception(f"Invalid response (no task_id): {response_data}")

    return response_data["task_id"]


def get_status(task_id):
    """
    Get processing status of a task.
    """

    res = requests.get(f"{BASE_URL}/analysis/status/{task_id}")

    if res.status_code != 200:
        raise Exception(f"Status check failed: {res.text}")

    return res.json()


def get_result(task_id):
    """
    Get final result of a completed task.
    """

    res = requests.get(f"{BASE_URL}/analysis/result/{task_id}")

    if res.status_code != 200:
        raise Exception(f"Result fetch failed: {res.text}")

    return res.json()
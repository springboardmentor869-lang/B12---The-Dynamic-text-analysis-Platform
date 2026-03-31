from fastapi import FastAPI, UploadFile, File
import shutil
import os
import fitz

app = FastAPI(title="Topic Inference API")

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_text(file_path):
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()
    return text


def infer_topic(text):
    text = text.lower()

    if "stock" in text or "market" in text:
        return "Finance"
    elif "doctor" in text or "health" in text:
        return "Healthcare"
    elif "ai" in text or "technology" in text:
        return "Technology"
    else:
        return "General"


@app.post("/topic")
async def topic_api(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_text(file_path)
        topic = infer_topic(text)

        return {
            "status": "success",
            "filename": file.filename,
            "topic": topic
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
from fastapi import FastAPI, UploadFile, File
import shutil
import os
import fitz

app = FastAPI(title="Summarization API")

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_text(file_path):
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()
    return text


def summarize_text(text):
    sentences = text.split(".")
    return ". ".join(sentences[:3])


@app.post("/summarize")
async def summarize_api(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_text(file_path)
        summary = summarize_text(text)

        return {
            "status": "success",
            "filename": file.filename,
            "summary": summary
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
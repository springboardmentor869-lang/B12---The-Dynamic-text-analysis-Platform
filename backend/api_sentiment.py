from fastapi import FastAPI, UploadFile, File
import shutil
import os
import fitz

app = FastAPI(title="Sentiment API")

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_text(file_path):
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()
    return text


def analyze_sentiment(text):
    text = text.lower()

    if "good" in text or "love" in text or "excellent" in text:
        return "Positive 😊"
    elif "bad" in text or "hate" in text or "worst" in text:
        return "Negative 😞"
    else:
        return "Neutral 😐"


@app.post("/sentiment")
async def sentiment_api(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_text(file_path)
        result = analyze_sentiment(text)

        return {
            "status": "success",
            "filename": file.filename,
            "sentiment": result
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
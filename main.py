from fastapi import FastAPI, UploadFile, File
import shutil
import os
import fitz

app = FastAPI(title="Dynamic Text Analysis API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================
# COMMON FUNCTION
# =========================
def extract_text(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


# =========================
# 1. CONVERT
# =========================
@app.post("/convert")
async def convert_api(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        doc = fitz.open(file_path)
        markdown = ""

        for i, page in enumerate(doc):
            markdown += f"\n\n## Page {i+1}\n\n{page.get_text()}"

        doc.close()

        return {
            "status": "success",
            "markdown": markdown
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        os.remove(file_path)


# =========================
# 2. SUMMARIZE
# =========================
@app.post("/summarize")
async def summarize_api(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_text(file_path)
        sentences = text.split(".")
        summary = ". ".join(sentences[:3])

        return {
            "status": "success",
            "summary": summary
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        os.remove(file_path)


# =========================
# 3. SENTIMENT
# =========================
@app.post("/sentiment")
async def sentiment_api(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_text(file_path).lower()

        if "good" in text or "love" in text:
            result = "Positive 😊"
        elif "bad" in text or "hate" in text:
            result = "Negative 😞"
        else:
            result = "Neutral 😐"

        return {
            "status": "success",
            "sentiment": result
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        os.remove(file_path)


# =========================
# 4. TOPIC
# =========================
@app.post("/topic")
async def topic_api(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_text(file_path).lower()

        if "stock" in text or "market" in text:
            topic = "Finance"
        elif "doctor" in text or "health" in text:
            topic = "Healthcare"
        elif "ai" in text or "technology" in text:
            topic = "Technology"
        else:
            topic = "General"

        return {
            "status": "success",
            "topic": topic
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        os.remove(file_path)
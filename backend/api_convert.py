from fastapi import FastAPI, UploadFile, File
import shutil, os
import fitz

app = FastAPI()
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def convert_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for i, page in enumerate(doc):
        text += f"\n\n## Page {i+1}\n\n{page.get_text()}"
    doc.close()
    return text

@app.post("/convert")
async def convert_api(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = convert_pdf(path)
        return {"markdown": result}
    finally:
        os.remove(path)
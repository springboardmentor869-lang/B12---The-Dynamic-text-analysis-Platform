"""
api_convert.py - FastAPI endpoint for document-to-markdown conversion.

Provides:
- REST API endpoint to upload documents (PDF/DOCX)
- Extract text using convert_document.extract_with_fallback
- Convert extracted text into simple Markdown format
- Return Markdown response and save file to disk

Endpoint:
- POST /convert-file

Pipeline:
1. Receive uploaded file
2. Save file temporarily
3. Extract text using fallback parser
4. Convert text → Markdown
5. Save Markdown file to results directory
6. Return Markdown in API response

Requires:
- fastapi               - API framework
- shutil                - file handling (stream copy)
- os                    - filesystem operations
- convert_document.py   - text extraction utility

Input:
- Multipart file upload (.pdf or .docx)

Output:
- JSON response:
    {
        "filename": "...",
        "markdown": "..."
    }

- Saved file:
    results/api_md/*.md

Run (example with uvicorn):
    uvicorn api:app --reload
"""

from fastapi import APIRouter, UploadFile, File
import os
import shutil
from convert_document import extract_with_fallback

router = APIRouter()

OUTPUT_DIR = "results/api_md"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Convert plain text into simple Markdown format
def text_to_markdown(text: str) -> str:
    lines = text.split("\n")
    md_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            md_lines.append("")
            continue

        if len(line) < 60:
            md_lines.append(f"## {line}")
        else:
            md_lines.append(line)

    return "\n".join(md_lines)


# API Endpoint
@router.post("/convert-file")

# Upload file → extract text → convert to markdown
async def convert_file(file: UploadFile = File(...)):

    temp_path = f"temp_{file.filename}"

    try:
        # Save uploaded file to disk
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text using fallback parser
        text = extract_with_fallback(temp_path)

        if not text.strip():
            return {"error": "Could not extract text"}

        markdown = text_to_markdown(text)

        output_name = file.filename.replace(".pdf", ".md").replace(".docx", ".md")
        output_path = os.path.join(OUTPUT_DIR, output_name)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        # Return response
        return {
            "filename": file.filename,
            "markdown": markdown
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
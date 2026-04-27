"""
API endpoint for document-to-markdown conversion.
POST /api/convert-file
"""

from fastapi import APIRouter, UploadFile, File
import os
import shutil
from fastapi.responses import FileResponse
from backend.convert_document import extract_with_fallback

router = APIRouter()

OUTPUT_DIR = "results/api_md"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def text_to_markdown(text: str) -> str:
    """Convert extracted text to Markdown."""
    lines = text.split("\n")
    md_lines = []
    
    for line in lines:
        line = line.rstrip()
        
        if not line:
            md_lines.append("")
            continue
        
        if (line.isupper() and 
            len(line) < 100 and 
            len(line.split()) >= 2):
            md_lines.append(f"\n## {line}\n")
        else:
            md_lines.append(line)
    
    return "\n".join(md_lines)


@router.post("/convert-file")

async def convert_file(file: UploadFile = File(...)):
    """Convert PDF/DOCX to Markdown."""
    
    temp_path = f"temp_{file.filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = extract_with_fallback(temp_path)
        
        if not text.strip():
            return {"error": "Could not extract text"}
        
        markdown = text_to_markdown(text)
        
        output_name = file.filename.rsplit(".", 1)[0] + ".md"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        # Save TXT version also
        txt_output_name = file.filename.rsplit(".", 1)[0] + ".txt"
        txt_output_path = os.path.join(OUTPUT_DIR, txt_output_name)

        with open(txt_output_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        return {
            "status": "success",
            "filename": file.filename,
            "markdown": markdown,
            "download_md": f"/download/{output_name}",
            "download_txt": f"/download/{output_name.replace('.md', '.txt')}"
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/download/{filename}")

async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
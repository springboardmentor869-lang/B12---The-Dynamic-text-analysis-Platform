import fitz
import sys
import logging
from pathlib import Path
from typing import List
from fastapi import HTTPException

# Configure a logger so you can see the switch in your terminal
logger = logging.getLogger(__name__)

# Path hack to reach task3
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

try:
    from task3.doc_parser import convert_bytes_to_markdown
    HAS_TASK3 = True
except ImportError:
    HAS_TASK3 = False

def extract_text_smart(file_bytes: bytes) -> str:
    """Attempts Docling, but catches memory crashes to use PyMuPDF fallback."""
    
    # 1. Try High-Quality Docling
    if HAS_TASK3:
        try:
            logger.info("Attempting Docling extraction...")
            return convert_bytes_to_markdown(file_bytes)
        except (Exception, MemoryError) as e:
            # This catches both Python and low-level memory errors
            logger.warning(f"Docling failed on memory/alloc (Error: {e}). Switching to PyMuPDF...")
    
    # 2. PyMuPDF Fallback (Lightweight & Reliable)
    logger.info("Running PyMuPDF fallback extraction...")
    text = ""
    try:
        # Open PDF directly from bytes
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            # We add a small delay or check here if the PDF is massive, 
            # but fitz is usually fine.
            text += page.get_text() + "\n\n"
        doc.close()
        
        if not text.strip():
            raise ValueError("PyMuPDF extracted no text (possible scanned images).")
            
        return text.strip()
        
    except Exception as e:
        logger.error(f"Critical: Both parsers failed. {str(e)}")
        raise HTTPException(status_code=500, detail="Document processing failed on all levels.")

def chunk_text(text: str, chunk_size: int = 8000) -> List[str]:
    """
    Groups text into large blocks to drastically reduce the number of API calls.
    Defaults to 8000 characters to keep memory safe on an 8GB laptop.
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
    
    # If the PDF has no paragraph breaks, do a hard mathematical slice
    if not paragraphs:
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
    chunks = []
    current_chunk = ""
    
    # Greedy chunking: Keep adding paragraphs together until we hit the chunk_size limit
    for p in paragraphs:
        if len(current_chunk) + len(p) > chunk_size:
            # The chunk is full! Save it and start a new one
            chunks.append(current_chunk.strip())
            current_chunk = p + "\n\n"
        else:
            # There is still room in this chunk, add the paragraph
            current_chunk += p + "\n\n"
            
    # Don't forget to add the very last chunk!
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    return chunks
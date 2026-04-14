import os
import uuid
from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter
from core.config import settings


def parse_pdf_to_markdown(file_path: str) -> tuple[str, str]:
    """
    Parse PDF to Markdown using Docling.

    Args:
        file_path: Path to the PDF file

    Returns:
        tuple of (markdown_content, markdown_file_path)
    """
    converter = DocumentConverter()
    result = converter.convert(file_path)
    markdown_content = result.document.export_to_markdown()

    # Save to temp markdown directory with unique name
    unique_id = uuid.uuid4().hex[:8]
    md_file_path = settings.temp_markdown_dir / f"{unique_id}.md"

    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    return markdown_content, str(md_file_path)


def cleanup_temp_files(md_file_path: Optional[str] = None, pdf_file_path: Optional[str] = None):
    """Remove temporary files after processing."""
    if md_file_path and os.path.exists(md_file_path):
        try:
            os.remove(md_file_path)
        except OSError:
            pass

    if pdf_file_path and os.path.exists(pdf_file_path):
        try:
            os.remove(pdf_file_path)
        except OSError:
            pass
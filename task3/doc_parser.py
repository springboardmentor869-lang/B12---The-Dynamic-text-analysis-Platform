#task3 -Docling-based Document Parser
import os
from docling.document_converter import DocumentConverter

class DocumentParser:
    def __init__(self):
        # Expanded list of formats supported by Docling
        self.supported_formats = [
            '.pdf', '.docx', '.pptx', '.html', '.xhtml', '.xml', 
            '.jpg', '.jpeg', '.png', '.bmp'
        ]
        self.converter = DocumentConverter()

    def convert_to_text(self, input_path, output_dir="processed_data"):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        _, ext = os.path.splitext(input_path)
        
        # simple validation to ensure we only try to parse supported files
        if ext.lower() not in self.supported_formats:
            print(f"Skipping {input_path}: Unsupported format {ext}")
            return None

        filename = os.path.basename(input_path)
        output_filename = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.md")

        try:
            print(f"Processing: {filename}...")
            
            # The 'convert' method automatically detects the format (PDF, PPTX, HTML, etc.)
            result = self.converter.convert(input_path)
            
            # export_to_markdown preserves layout (tables/headers) better than raw text
            extracted_text = result.document.export_to_markdown()

            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            
            return output_filename

        except Exception as e:
            print(f"Error converting {filename}: {str(e)}")
            return None

import fitz
import os
import tempfile
import gc  # Add garbage collection
from docling.document_converter import DocumentConverter

def convert_bytes_to_markdown(file_bytes: bytes, file_extension: str = ".pdf") -> str:
    """
    Advanced 'Chunk & Stitch' Docling Parser.
    Allows full OCR on massive PDFs without causing Out-Of-Memory (OOM) crashes.
    """
    # If it's not a PDF, just run it normally
    if not file_extension.lower().endswith('.pdf'):
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name
        try:
            converter = DocumentConverter()
            result = converter.convert(temp_path)
            return result.document.export_to_markdown()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # --- THE CHUNK & STITCH LOGIC FOR PDFs ---
    CHUNK_SIZE = 2  # Reduced from 5 to 2 pages at a time to prevent memory issues
    full_markdown = ""
    
    # Load the full PDF into PyMuPDF (which uses almost no RAM)
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    total_pages = len(doc)
    
    # Initialize Docling ONCE with full OCR enabled
    converter = DocumentConverter()
    
    print(f"Starting Chunk & Stitch OCR on {total_pages} pages (chunk size: {CHUNK_SIZE})...")

    for start_page in range(0, total_pages, CHUNK_SIZE):
        end_page = min(start_page + CHUNK_SIZE, total_pages)
        print(f" -> Docling OCR Processing pages {start_page + 1} to {end_page}...")
        
        # 1. Slice out a small chunk of pages
        chunk_doc = fitz.open()
        chunk_doc.insert_pdf(doc, from_page=start_page, to_page=end_page - 1)
        
        # 2. Save the tiny chunk to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_chunk:
            chunk_doc.save(temp_chunk.name)
            chunk_path = temp_chunk.name
        chunk_doc.close()
        
        # 3. Feed the tiny chunk to Docling
        try:
            result = converter.convert(chunk_path)
            # Append the extracted markdown, adding a visual page break
            full_markdown += result.document.export_to_markdown() + "\n\n---\n\n"
        except Exception as e:
            error_msg = str(e)
            if "bad_alloc" in error_msg or "memory" in error_msg.lower():
                print(f"    [!] Memory error on chunk {start_page+1}-{end_page}, trying single page processing...")
                # Try processing each page individually if chunk fails
                chunk_doc = fitz.open()
                chunk_doc.insert_pdf(doc, from_page=start_page, to_page=end_page - 1)
                
                for page_idx in range(chunk_doc.page_count):
                    single_page_doc = fitz.open()
                    single_page_doc.insert_pdf(chunk_doc, from_page=page_idx, to_page=page_idx)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_single:
                        single_page_doc.save(temp_single.name)
                        single_path = temp_single.name
                    
                    try:
                        result = converter.convert(single_path)
                        full_markdown += result.document.export_to_markdown() + "\n\n---\n\n"
                        print(f"      ✓ Page {start_page + page_idx + 1} processed individually")
                    except Exception as single_e:
                        print(f"      ✗ Failed page {start_page + page_idx + 1}: {single_e}")
                        # Skip this page and continue
                    finally:
                        single_page_doc.close()
                        if os.path.exists(single_path):
                            os.remove(single_path)
                
                chunk_doc.close()
            else:
                print(f"    [!] Warning: Docling failed on chunk {start_page+1}-{end_page}: {e}")
        finally:
            # 4. Clean up the temp file to free disk space
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
            # Force garbage collection to free memory
            gc.collect()

    doc.close()
    
    if not full_markdown.strip():
        print("Docling Chunk & Stitch failed to extract any text. Falling back to PyMuPDF...")
        # Fallback: Use PyMuPDF for basic text extraction
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        full_markdown = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                full_markdown += f"## Page {page_num + 1}\n\n{text}\n\n---\n\n"
        doc.close()
        
        if not full_markdown.strip():
            raise ValueError("Both Docling and PyMuPDF fallback failed to extract any text.")
        
    return full_markdown

if __name__ == "__main__":
    parser = DocumentParser()
    
  
    input_folder = "../assets"
    

    if os.path.exists(input_folder):
        files_to_process = os.listdir(input_folder)
        
        print(f"Found {len(files_to_process)} files in '{input_folder}'...")
        
        for filename in files_to_process:

            file_path = os.path.join(input_folder, filename)

            if os.path.isfile(file_path):
                output_file = parser.convert_to_text(file_path)
                if output_file:
                    print(f"  -> Saved to: {output_file}")
    else:
        print(f"ERROR: The folder '{input_folder}' does not exist.")

  
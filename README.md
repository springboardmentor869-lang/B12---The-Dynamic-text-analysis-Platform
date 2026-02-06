```markdown
# dynamic-text-analyser

This repository contains tools to:
- Evaluate PDF/DOCX text extraction libraries using Word Error Rate (WER)
- Extract text from PDF and DOCX and export to `.txt` or `.md`

Quick start:
1. Create and activate virtual environment:
   - python -m venv .venv
   - PowerShell: .\.venv\Scripts\Activate.ps1
2. Install dependencies:
   - pip install -r requirements.txt
3. Put sample documents in `data/pdfs/` and `data/docx/`; create ground-truth `.txt` files in `data/ground_truth/` with same basenames.
4. Run evaluation:
   - python evaluate_parsers.py
5. Convert a document:
   - python convert_document.py input.pdf --out results/extracted/myfile.txt --parser pymupdf

See the repository for parser implementations, evaluation scripts, and guidance on OCR/poppler.
```
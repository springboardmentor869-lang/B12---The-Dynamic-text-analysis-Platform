# Document Processing & Text Preprocessing Toolkit

This repository provides a set of Python scripts for extracting text from documents, preprocessing it for NLP tasks, evaluating parser accuracy, and generating token tables with linguistic annotations.

## Overview

The toolkit includes:

- **`parsers.py`**  
  Minimal in‑process parsers for PDF, DOCX, and OCR extraction.  
  - `pymupdf` → uses [PyMuPDF](https://pymupdf.readthedocs.io/)  
  - `docx` → uses [python-docx](https://python-docx.readthedocs.io/)  
  - `ocr` → uses [pytesseract](https://pypi.org/project/pytesseract/) + [Pillow](https://pillow.readthedocs.io/)

- **`convert_document.py`**  
  Conversion utility that wraps `PARSERS` with fallback logic.  
  Provides `extract_with_fallback(path, parser=None)` and a CLI for converting documents to plain text.

- **`preprocess_text.py`**  
  Preprocesses extracted text:  
  - Cleans punctuation, numbers, and hyphenation  
  - Tokenizes and removes stopwords  
  - Produces stemmed and lemmatized outputs

- **`evaluate_parsers.py`**  
  Evaluates parser performance using Word Error Rate (WER) against reference text files.  
  Outputs results to CSV.

- **`tokens_table.py`**  
  Generates a CSV table with token, POS tag, stem, and lemma.  
  Supports both NLTK and spaCy lemmatization.

## Installation

Clone the repository and install dependencies:

git clone <repo-url>
cd <repo-dir>
pip install -r requirements.txt
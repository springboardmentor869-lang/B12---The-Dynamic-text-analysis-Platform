#!/usr/bin/env python3
"""
convert_document.py - simple document conversion utility.

This module provides a flexible document-to-text extraction system.
It can:
    - Extract text from PDF, DOCX, and TXT files
    - Automatically fall back to alternative parsers if one fails
    - Be used as an importable function
    - Be executed as a command-line tool (CLI)

CLI: python convert_document.py <input> --out <outfile> [--parser <name>]

Default Behavior:
- For PDFs → tries 'pymupdf' first, then 'ocr'
- For DOCX → uses 'docx'
- For TXT → reads file directly
- If parser specified → only that parser is used

Required Libraries:
- argparse  → Command-line argument parsing
- os        → File and directory handling
- parsers   → Custom module containing parser functions
- typing    → Type hints for clarity

Input:
- input_path (str): Path to input file (.pdf, .docx, .txt)
- parser (Optional[str]): Preferred parser name (optional)

Output:
- Extracted text written to output file
"""

from typing import Optional
import os
import argparse

from .parsers import PARSERS

# Extract text from a document with optional parser fallback logic.
def extract_with_fallback(input_path: str, parser: Optional[str] = None) -> str:
    
    ext = os.path.splitext(input_path)[1].lower()
    
    # If file is plain text, read it directly
    if ext == ".txt":
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                with open(input_path, "r", encoding=enc) as f:
                    return f.read()
            except Exception:
                continue
        
        # Fallback with error replacement
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    # Determine parser order
    if parser:
        order = [parser]
    else:
        if ext == ".pdf":
            order = ["pymupdf", "ocr"]
        elif ext == ".docx":
            order = ["docx"]
        else:
            order = list(PARSERS.keys())

    last_err = None

    # Try parsers in defined order
    for p in order:
        if p not in PARSERS:
            continue
        try:
            text = PARSERS[p](input_path)
            if text and text.strip():
                return text
        except Exception as e:
            last_err = e
            continue

    # Raise error if all parsers failed
    if last_err:
        raise RuntimeError(
            f"No parser succeeded for {input_path}. Last error: {last_err}"
        )
    
    return ""

# CLI entry point for document conversion.
def main():
    
    # Configure command-line argument parser
    ap = argparse.ArgumentParser(prog="convert_document.py")
    ap.add_argument("input", help="Input file (.pdf, .docx, .txt)")
    ap.add_argument("--out", required=True, help="Output text path (.txt or .md)")
    ap.add_argument("--parser", help="Preferred parser name (pymupdf, ocr, docx)")
    
    # Parse arguments
    args = ap.parse_args()

    # Extract text using fallback mechanism
    txt = extract_with_fallback(args.input, parser=args.parser)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    
    with open(args.out, "w", encoding="utf8") as f:
        f.write(txt)

if __name__ == "__main__":
    main()
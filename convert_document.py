#!/usr/bin/env python3
"""
convert_document.py - simple conversion utility.

Provides:
- extract_with_fallback(input_path, parser=None) -> str  (importable)
- CLI: python convert_document.py <input> --out <outfile> [--parser <name>]

Default behavior:
- For PDFs try 'pymupdf' then 'ocr'.
- For DOCX use 'docx'.
- For TXT simply read the file.
"""
from typing import Optional
import os
import argparse

from parsers import PARSERS

def extract_with_fallback(input_path: str, parser: Optional[str] = None) -> str:
    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".txt":
        # Read text file robustly
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                with open(input_path, "r", encoding=enc) as f:
                    return f.read()
            except Exception:
                continue
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    # choose parser order
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

    if last_err:
        raise RuntimeError(f"No parser succeeded for {input_path}. Last error: {last_err}")
    return ""

def main():
    ap = argparse.ArgumentParser(prog="convert_document.py")
    ap.add_argument("input", help="Input file (.pdf, .docx, .txt)")
    ap.add_argument("--out", required=True, help="Output text path (.txt or .md)")
    ap.add_argument("--parser", help="Preferred parser name (pymupdf, ocr, docx)")
    args = ap.parse_args()

    txt = extract_with_fallback(args.input, parser=args.parser)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf8") as f:
        f.write(txt)

if __name__ == "__main__":
    main()
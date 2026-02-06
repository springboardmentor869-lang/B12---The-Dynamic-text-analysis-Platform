import argparse
import os
from parsers import PARSERS

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Input file (.pdf or .docx)")
    ap.add_argument("--out", required=True, help="Output file (.txt or .md)")
    ap.add_argument("--parser", default="pymupdf", help="Parser to use")
    args = ap.parse_args()

    parser_name = args.parser
    if parser_name not in PARSERS:
        raise SystemExit(f"Unknown parser: {parser_name}")

    text = PARSERS[parser_name](args.input)
    with open(args.out, "w", encoding="utf8") as f:
        f.write(text)
    print(f"Wrote extracted text to {args.out}")

if __name__ == "__main__":
    main()
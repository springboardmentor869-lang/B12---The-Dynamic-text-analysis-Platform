#!/usr/bin/env python3
"""
preprocess_text.py - simple text preprocessing.

For each input file this script:
 - extracts text (via convert_document.extract_with_fallback)
 - cleans (remove punctuation, numbers, de-hyphen)
 - tokenizes and removes English stopwords
 - produces two outputs:
     results/preprocessed/<base>.stemmed.txt
     results/preprocessed/<base>.lemmatized.txt

Minimal, single-threaded, no intermediate files.
"""
from typing import List
import os
import re
import argparse
import nltk

# prefer local nltk_data
nltk.data.path.insert(0, os.path.join(os.getcwd(), "nltk_data"))

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# extraction helper (import convert_document)
try:
    from convert_document import extract_with_fallback
except Exception:
    extract_with_fallback = None  # will raise if not present

def ensure_nltk_data() -> None:
    resources = {
        "punkt": "tokenizers/punkt",
        "stopwords": "corpora/stopwords",
        "wordnet": "corpora/wordnet",
        "omw-1.4": "corpora/omw-1.4",
        "averaged_perceptron_tagger": "taggers/averaged_perceptron_tagger",
    }
    local = os.path.join(os.getcwd(), "nltk_data")
    os.makedirs(local, exist_ok=True)
    if local not in nltk.data.path:
        nltk.data.path.insert(0, local)
    for name, path in resources.items():
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, download_dir=local)

def clean_text(text: str, remove_numbers: bool = True) -> str:
    text = re.sub(r"-\s*\n\s*", "", text)   # de-hyphen
    text = text.replace("\n", " ")
    text = text.lower()
    if remove_numbers:
        text = re.sub(r"\d+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize_and_remove_stopwords(text: str, extra_stopwords: List[str] = None) -> List[str]:
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    if extra_stopwords:
        stop_words.update(w.lower() for w in extra_stopwords)
    return [t for t in tokens if t and t.lower() not in stop_words]

def stem_tokens(tokens: List[str]) -> List[str]:
    stemmer = PorterStemmer()
    return [stemmer.stem(t) for t in tokens]

def lemmatize_tokens(tokens: List[str]) -> List[str]:
    # POS tagging helps WordNet lemmatizer
    pos_tags = nltk.pos_tag(tokens)
    lemmatizer = WordNetLemmatizer()
    def tagmap(tag: str) -> str:
        if tag.startswith("J"):
            return "a"
        if tag.startswith("V"):
            return "v"
        if tag.startswith("N"):
            return "n"
        if tag.startswith("R"):
            return "r"
        return "n"
    return [lemmatizer.lemmatize(t, pos=tagmap(tag)) for t, tag in pos_tags]

def write_joined(path: str, tokens: List[str]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        f.write(" ".join(tokens))

def process_one_file(path: str, outdir: str = "results/preprocessed", remove_numbers: bool = True, extra_stopwords: List[str] = None) -> None:
    if extract_with_fallback is None:
        raise RuntimeError("convert_document.extract_with_fallback not available; ensure convert_document.py exists")
    ensure_nltk_data()
    raw = extract_with_fallback(path)
    base = os.path.splitext(os.path.basename(path))[0]
    os.makedirs(outdir, exist_ok=True)

    if not raw or not raw.strip():
        # write empty outputs for consistency
        write_joined(os.path.join(outdir, f"{base}.stemmed.txt"), [])
        write_joined(os.path.join(outdir, f"{base}.lemmatized.txt"), [])
        return

    cleaned = clean_text(raw, remove_numbers=remove_numbers)
    tokens = tokenize_and_remove_stopwords(cleaned, extra_stopwords=extra_stopwords)
    stems = stem_tokens(tokens)
    lemmas = lemmatize_tokens(tokens)

    write_joined(os.path.join(outdir, f"{base}.stemmed.txt"), stems)
    write_joined(os.path.join(outdir, f"{base}.lemmatized.txt"), lemmas)
    print(f"Wrote: {base}.stemmed.txt and {base}.lemmatized.txt in {outdir}")

def main():
    ap = argparse.ArgumentParser(prog="preprocess_text.py")
    ap.add_argument("inputs", nargs="*", help="Input files. If omitted, process files in data/pdfs and data/docx")
    ap.add_argument("--outdir", default="results/preprocessed")
    ap.add_argument("--no-remove-numbers", dest="remove_numbers", action="store_false", help="Do not remove numbers")
    ap.add_argument("--extra-stopwords", nargs="*", default=[])
    ap.add_argument("--pdfs-dir", default="data/pdfs")
    ap.add_argument("--docx-dir", default="data/docx")
    args = ap.parse_args()

    if args.inputs:
        inputs = args.inputs
    else:
        inputs = []
        if os.path.isdir(args.pdfs_dir):
            inputs += [os.path.join(args.pdfs_dir, f) for f in os.listdir(args.pdfs_dir) if f.lower().endswith(".pdf")]
        if os.path.isdir(args.docx_dir):
            inputs += [os.path.join(args.docx_dir, f) for f in os.listdir(args.docx_dir) if f.lower().endswith(".docx")]
        inputs = sorted(inputs)

    if not inputs:
        print("No input files found.")
        return

    for p in inputs:
        try:
            process_one_file(p, outdir=args.outdir, remove_numbers=args.remove_numbers, extra_stopwords=args.extra_stopwords)
        except Exception as e:
            print(f"[ERROR] {p}: {e}")

if __name__ == "__main__":
    main()
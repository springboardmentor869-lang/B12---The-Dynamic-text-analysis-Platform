#!/usr/bin/env python3
"""
token_table.py

This script generates a CSV table containing:
    - Token
    - Part-of-Speech (POS)
    - Stem
    - Lemma

It can operate in two modes:
1. Using a tokens.nostop.txt file (one token per line)
2. Using raw/cleaned text (internally tokenizes + removes stopwords)

Libraries Used:
- argparse          : Command-line argument parsing
- os                : File handling
- csv               : CSV file writing
- nltk              : Tokenization, POS tagging, stemming, lemmatization
- spaCy (optional)  : Improved lemmatization

NLTK Resources Required:
- punkt
- stopwords
- wordnet
- omw-1.4
- averaged_perceptron_tagger

Usage:
  # Using tokens file produced by preprocess_text.py
  python tokens_table.py results/preprocessed/ASD.tokens.nostop.txt --out results/preprocessed/ASD.tokens.csv --use-spacy

  # Or provide any plain text input (one or many lines). The script will tokenize then remove stopwords internally:
  python tokens_table.py --text-file results/preprocessed/ASD.cleaned.txt --out results/preprocessed/ASD.tokens.csv --use-spacy

Output:
    A structured CSV file with linguistic features.
"""

import argparse
import os
import csv
from typing import List

import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import stopwords

# spaCy optional
try:
    import spacy
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False

# Helpers functions

# Reads a tokens file (one token per line)
def read_tokens_file(path: str) -> List[str]:
    with open(path, "r", encoding="utf8") as f:
        return [line.strip() for line in f if line.strip()]

# Tokenizes raw text using NLTK.
def tokenize_text(text: str) -> List[str]:
    from nltk.tokenize import word_tokenize
    return word_tokenize(text)

# Removes English stopwords and optional extra stopwords
def remove_stopwords(tokens: List[str], extra_stopwords: List[str] = None) -> List[str]:
    stop_words = set(stopwords.words("english"))
    if extra_stopwords:
        stop_words.update(w.lower() for w in extra_stopwords)
    return [t for t in tokens if t.lower() not in stop_words]

# Maps Penn Treebank POS tags to WordNet POS format
def penn_to_wordnet_pos(tag: str) -> str:
    if tag.startswith("J"):
        return "a" # adjective
    elif tag.startswith("V"):
        return "v" # verb
    elif tag.startswith("N"):
        return "n" # noun
    elif tag.startswith("R"):
        return "r" # adverb
    else:
        return "n"

# Lemmatizes tokens using NLTK WordNet lemmatizer.
def lemmatize_tokens_nltk(tokens: List[str], pos_tags: List[tuple]) -> List[str]:
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for tok, tag in pos_tags:
        wn_pos = penn_to_wordnet_pos(tag)
        lemmas.append(lemmatizer.lemmatize(tok, pos=wn_pos))
    return lemmas

# Lemmatizes tokens using spaCy model
def lemmatize_tokens_spacy(tokens: List[str], nlp) -> List[str]:
    doc = nlp(" ".join(tokens))
    return [t.lemma_ for t in doc]

def main():
    
    ap = argparse.ArgumentParser()
    
    ap.add_argument("input", nargs="?", help="Path to tokens.nostop.txt or to any text file (if --text-file used). If omitted, use --text-file.")
    ap.add_argument("--text-file", help="If provided, use this cleaned/raw text file and tokenize+remove stopwords internally")
    ap.add_argument("--out", required=True, help="Output CSV path")
    ap.add_argument("--use-spacy", action="store_true", help="Use spaCy for lemmatization (better). Requires en_core_web_sm.")
    ap.add_argument("--extra-stopwords", nargs="*", default=[], help="Extra stopwords to remove")
    
    args = ap.parse_args()

    # Ensure common NLTK resources are present (should already be via preprocess script)
    nltk_required = ["punkt", "stopwords", "wordnet", "omw-1.4", "averaged_perceptron_tagger"]
    for res in nltk_required:
        try:
            nltk.data.find(f"tokenizers/{res}") if res == "punkt" else nltk.data.find(f"corpora/{res}")
        except LookupError:
            print(f"[nltk] Missing {res}, downloading...")
            nltk.download(res)

    # Load tokens
    tokens = []
    if args.text_file:
        txt = open(args.text_file, "r", encoding="utf8").read()
        tokens_raw = tokenize_text(txt)
        tokens = remove_stopwords(tokens_raw, extra_stopwords=args.extra_stopwords)
    elif args.input:
        # Assume tokens file (one token per line)
        tokens = read_tokens_file(args.input)
    else:
        raise SystemExit("Provide either a tokens file path or --text-file")

    if not tokens:
        print("[WARN] No tokens found. Exiting.")
        return

    # Linguistic Processing

    # POS tagging
    pos_tags = nltk.pos_tag(tokens)

    # Stem
    stemmer = PorterStemmer()
    stems = [stemmer.stem(t) for t in tokens]

    # Lemmatize (spaCy if available and requested)
    if args.use_spacy and SPACY_AVAILABLE:
        nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        lemmas = lemmatize_tokens_spacy(tokens, nlp)
    else:
        lemmas = lemmatize_tokens_nltk(tokens, pos_tags)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf8") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["token", "pos", "stem", "lemma"])
        for tok, pos, stem, lem in zip(tokens, [p for (_, p) in pos_tags], stems, lemmas):
            writer.writerow([tok, pos, stem, lem])

    print(f"Wrote token table to: {args.out}")
    print(f"Tokens: {len(tokens)}")

if __name__ == "__main__":
    main()
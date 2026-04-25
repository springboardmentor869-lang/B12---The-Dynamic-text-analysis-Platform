import re

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_into_chunks(text, chunk_size=500):
    return [
        text[i:i+chunk_size].strip()
        for i in range(0, len(text), chunk_size)
        if text[i:i+chunk_size].strip()
    ]

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 15]
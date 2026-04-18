from transformers import pipeline
import re
import torch

# Determine device (GPU if available, else CPU)
device = 0 if torch.cuda.is_available() else -1

# ── Use DistilBART (2x faster than bart-large-cnn, similar quality) ──
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=device)

# DistilBART tokenizer max input is ~1024 tokens ≈ ~3500 chars
CHUNK_CHAR_LIMIT = 3000
MAX_CHUNKS = 3


def _chunk_text(text, limit=CHUNK_CHAR_LIMIT):
    """Split text into chunks at sentence boundaries."""
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text.strip())
            break
        # Find the last period/sentence-end within the limit
        cut = text[:limit].rfind(". ")
        if cut == -1 or cut < limit // 2:
            cut = text[:limit].rfind(" ")
        if cut == -1:
            cut = limit
        else:
            cut += 1  # include the period/space
        chunks.append(text[:cut].strip())
        text = text[cut:].strip()
    return chunks


def summarize_text(text):
    """
    Summarize the full document by chunking and summarizing each part,
    then combining into a comprehensive summary.
    """
    try:
        if not text or len(text.strip()) < 50:
            return "Text is too short to summarize."

        chunks = _chunk_text(text)[:MAX_CHUNKS]
        # Filter out very short chunks
        chunks = [c for c in chunks if len(c.strip()) >= 40]

        if not chunks:
            return "Text is too short to summarize."

        if len(chunks) == 1:
            # Single chunk — generate a longer summary directly
            input_len = len(chunks[0].split())
            result = summarizer(
                chunks[0],
                max_length=min(300, max(150, input_len // 2)),
                min_length=80,
                do_sample=False,
            )
            return result[0]["summary_text"]

        # ── BATCH inference: summarize all chunks in one call ──
        max_lengths = [min(200, max(100, len(c.split()) // 2)) for c in chunks]
        results = summarizer(
            chunks,
            max_length=max(max_lengths),
            min_length=50,
            do_sample=False,
            batch_size=4,
        )
        partial_summaries = [r["summary_text"] for r in results]

        combined = " ".join(partial_summaries)

        # If combined is long enough, do a final pass to make it coherent
        if len(combined.split()) > 250:
            final = summarizer(
                combined[:CHUNK_CHAR_LIMIT],
                max_length=350,
                min_length=120,
                do_sample=False,
            )
            return final[0]["summary_text"]

        return combined

    except Exception as e:
        print("Summarization error:", e)
        return "Summary could not be generated."
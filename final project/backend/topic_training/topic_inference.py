from transformers import pipeline
import re
import torch

# Determine device (GPU if available, else CPU)
device = 0 if torch.cuda.is_available() else -1

# Using a reliable and fast distilled model for zero-shot classification
classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3", device=device)

TOPIC_LABELS = [
    "Artificial Intelligence", 
    "Healthcare", 
    "Education", 
    "Technology", 
    "Business", 
    "Legal", 
    "Environment"
]

# -------------------------------------------------------
# TEXT PREPROCESSING
# -------------------------------------------------------

def preprocess_text(text):
    # Keep it simple for transformer models as they like context
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_chunks(text, chunk_size=800):
    return [
        text[i:i+chunk_size].strip()
        for i in range(0, len(text), chunk_size)
        if len(text[i:i+chunk_size].strip()) > 50
    ]


# -------------------------------------------------------
# MAIN DOCUMENT CLASSIFICATION
# -------------------------------------------------------

def classify_document(text):
    if not text or len(text.strip()) < 20:
        return {
            "dominant_topic": "General",
            "avg_score": 0.0,
            "topics": [],
            "chunk_results": [],
            "report": "Document is too short for meaningful topic analysis."
        }

    # Analyze the overall document (first 1000 chars for speed)
    sample = text[:1000]
    try:
        result = classifier(sample, candidate_labels=TOPIC_LABELS, multi_label=False)
        
        dominant_topic = result["labels"][0]
        avg_score = round(result["scores"][0], 4)
        
        topic_list = []
        for i in range(min(5, len(result["labels"]))):
            topic_list.append({
                "topic_id": i,
                "topic": result["labels"][i],
                "score": round(result["scores"][i], 4),
                "avg_score": round(result["scores"][i], 4)
            })

        # Chunk-level analysis
        chunks = split_into_chunks(text)[:4] # Reduced to 4 chunks for speed
        chunk_results = []
        
        if chunks:
            # Batch process chunks
            batch_results = classifier(chunks, candidate_labels=TOPIC_LABELS, multi_label=False)
            
            # If only one chunk, batch_results is a dict, otherwise a list of dicts
            if isinstance(batch_results, dict):
                batch_results = [batch_results]
                
            for idx, res in enumerate(batch_results):
                chunk_results.append({
                    "chunk_id": idx + 1,
                    "text": chunks[idx][:200] + "...", # Truncate for dashboard
                    "topic": res["labels"][0],
                    "score": round(res["scores"][0], 4)
                })

        report = f"""
Topic Modeling Report:
The document has been semantically analyzed using a neural Zero-Shot classification model.
The dominant theme is "{dominant_topic}" with a confidence of {avg_score * 100:.1f}%.

Other significant themes detected include {", ".join([t["topic"] for t in topic_list[1:3]])}.
The model performed analysis across {len(chunk_results)} segments to verify internal thematic consistency.
""".strip()

        return {
            "dominant_topic": dominant_topic,
            "avg_score": avg_score,
            "topics": topic_list,
            "chunk_results": chunk_results,
            "report": report
        }

    except Exception as e:
        print("Topic Inference Error:", e)
        return {
            "dominant_topic": "General",
            "avg_score": 0.0,
            "topics": [],
            "chunk_results": [],
            "report": f"Topic analysis encountered an error: {str(e)}"
        }
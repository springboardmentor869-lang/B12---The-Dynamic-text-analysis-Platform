import requests
from utils.chunking import chunk_text
from core.config import OLLAMA_URL


# Make sure you have this model installed in Ollama via `ollama run qwen2.5:3b`
MODEL_NAME = "qwen2.5:3b"


def summarize(text: str, task_manager=None, task_id=None) -> dict:
    """
    Pipeline-compatible summarization using Ollama with Hierarchical synthesis.
    """

    if not text or not text.strip():
        return {
            "summary": "Text is empty.",
            "chunks": 0,
            "chunk_summaries": []
        }

    chunks = chunk_text(text, max_words=400) # Slightly larger chunks for better context

    summaries = []
    
    if task_manager and task_id:
        task_manager.update_progress(task_id, f"Summarizing 0 of {len(chunks)} chunks...", 10)

    for idx, chunk in enumerate(chunks, start=1):
        if task_manager and task_id:
            pct = 10 + int((idx / len(chunks)) * 70) # Leave 10% for final synthesis
            task_manager.update_progress(task_id, f"Summarizing segment {idx} of {len(chunks)}...", pct)
            
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": f"You are an expert summarizer. Produce a clear, concise summary of the following segment focusing on key points and factual data.\n\nSegment:\n{chunk}",
                    "stream": False
                },
                timeout=90 # Increased timeout
            )

            if response.status_code != 200:
                summaries.append(f"[Segment {idx} analysis skipped due to server load]")
                continue

            data = response.json()
            summary_text = data.get("response", "").strip()
            if summary_text:
                summaries.append(summary_text)

        except Exception as e:
            summaries.append(f"[Segment {idx} connection error: {str(e)}]")

    if not summaries:
        return {"summary": "Summarization failed for all segments.", "chunks": len(chunks), "chunk_summaries": []}

    # Step 2: Final Synthesis (Hierarchical)
    if len(summaries) > 1:
        if task_manager and task_id:
            task_manager.update_progress(task_id, "Synthesizing overall executive summary...", 90)
            
        combined_summaries = "\n\n".join(summaries)
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": f"You are a lead executive assistant. I will provide several summaries of document segments. Create a single, cohesive, and high-level Executive Summary that synthesizes all these points into one professional report. Focus on the main purpose and key takeaways.\n\nSummaries:\n{combined_summaries}",
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                final_summary = response.json().get("response", combined_summaries).strip()
            else:
                final_summary = combined_summaries
        except:
            final_summary = combined_summaries
    else:
        final_summary = summaries[0]

    return {
        "summary": final_summary,
        "chunks": len(chunks),
        "chunk_summaries": summaries
    }
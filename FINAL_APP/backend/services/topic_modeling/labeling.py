import requests
from core.config import OLLAMA_URL

OLLAMA_MODEL = "qwen2.5:3b"

def refine_topic_labels(topic_id, keywords, docs):
    """
    Generate a concise topic label based on keywords and representative documents.
    """
    
    prompt = f"""
Generate a concise 2-4 word topic label.

Keywords: {', '.join(keywords)}

Example text:
{docs[0][:500] if docs else ""}

Respond with ONLY the label.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()
        label = response.json().get("response", "").strip()
        # Clean up any potential AI chatter (like quotes or "The label is...")
        label = label.replace('"', '').replace("'", "")
        if ":" in label:
            label = label.split(":")[-1].strip()
            
        return label if label else f"Topic {topic_id}"

    except Exception as e:
        print(f"Ollama labeling error for topic {topic_id}: {e}")
        return f"Topic {topic_id}"
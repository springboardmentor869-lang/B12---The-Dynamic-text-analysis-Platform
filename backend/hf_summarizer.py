"""
hf_summarizer.py - Hugging Face API-based text summarization tool (BART version).

Changes:
- Switched model to facebook/bart-large-cnn
- Reduced chunk size for better stability
- Added timeout + retry logic
- Added delay between API calls
"""

import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

print("Loaded token:", HF_TOKEN)

# 🔥 Updated model
model = "facebook/bart-large-cnn"

input_folder = "results/preprocessed"
output_folder = "results/summaries_hf"

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in .env")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# ✅ Better chunk size for BART
def chunk_text(text, chunk_size=150):
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


# ✅ Robust summarization with retry + timeout
def summarize_chunk(chunk, retries=3):
    url = f"https://router.huggingface.co/hf-inference/models/{model}"

    payload = {
        "inputs": chunk,
        "parameters": {
            "max_length": 130,
            "min_length": 30,
            "do_sample": False
        }
    }

    for attempt in range(retries):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30  # ⏱ prevents hanging
            )

            if response.status_code == 200:
                return response.json()[0]["summary_text"]

            print(f"Retry {attempt+1}: Status {response.status_code}")
            time.sleep(2)

        except requests.exceptions.RequestException:
            print(f"Retry {attempt+1}: Network error")
            time.sleep(2)

    raise Exception("Failed after multiple retries")


# ✅ Process full text safely
def summarize_text(text):
    text = text[:5000]  # 🔒 safety limit

    chunks = chunk_text(text)
    summaries = []

    for i, chunk in enumerate(chunks):
        print(f"Summarizing chunk {i+1}/{len(chunks)}...")
        summary = summarize_chunk(chunk)
        summaries.append(summary)

        time.sleep(1)  # ⏳ avoid rate limiting

    return "\n".join(summaries)


def main():
    if not os.path.exists(input_folder):
        print("Input folder not found.")
        return

    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.endswith(".txt"):
            continue

        input_path = os.path.join(input_folder, filename)
        print(f"\nSummarizing: {input_path}")

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        try:
            summary = summarize_text(text)

            output_path = os.path.join(
                output_folder,
                filename.replace(".txt", "_bart_summary.txt")
            )

            with open(output_path, "w", encoding="utf-8") as out:
                out.write(summary)

            print(f"Saved to: {output_path}")

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
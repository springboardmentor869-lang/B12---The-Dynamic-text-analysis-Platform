"""
hf_summarizer.py - Hugging Face API-based text summarization tool.
This script:
    - Reads preprocessed text files from results/preprocessed
    - Splits long text into manageable chunks
    - Sends each chunk to Hugging Face Inference API
    - Uses google/pegasus-xsum for abstractive summarization
    - Saves summaries into results/summaries_hf

Model Used:
- google/pegasus-xsum → Transformer-based abstractive summarization model

Required Libraries:
- os         : File handling
- requests   : HTTP API calls
- dotenv     : Load environment variables from .env file

Environment Requirements:
- A .env file containing:
      HF_TOKEN=your_huggingface_api_token

Input:
- Text files (.txt) in results/preprocessed/

Output:
- Summary text files in results/summaries_hf/
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Hugging Face API token
HF_TOKEN = os.getenv("HF_TOKEN")

print("Loaded token:", os.getenv("HF_TOKEN"))

model = "google/pegasus-xsum"

input_folder = "results/preprocessed"
output_folder = "results/summaries_hf"

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in .env")

# Prepare request headers
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


# Split long text into smaller chunks of words
def chunk_text(text, chunk_size=350):

    words = text.split()
    chunks = []

    # Divide text into word-based chunks
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks

# Send a single text chunk to Hugging Face API for summarization.
def summarize_chunk(chunk):
    
    url = f"https://router.huggingface.co/hf-inference/models/{model}"

    payload = {
        "inputs": chunk,
        "parameters": {
            "max_length": 200,
            "min_length": 60,
            "do_sample": False
        }
    }

    # Send POST request to Hugging Face API
    response = requests.post(url, headers=headers, json=payload)

    # Handle API errors
    if response.status_code != 200:
        raise Exception(f"HF error {response.status_code}: {response.text}")

    return response.json()[0]["summary_text"]


# Summarize full text by processing it chunk by chunk.
def summarize_text(text):
    
    chunks = chunk_text(text)
    summaries = []

    # Process each chunk sequentially
    for i, chunk in enumerate(chunks):
        print(f"  Summarizing chunk {i+1}/{len(chunks)}...")
        summary = summarize_chunk(chunk)
        summaries.append(summary)

    # Combine chunk summaries
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
                filename.replace(".txt", "_pegasus_summary.txt")
            )

            with open(output_path, "w", encoding="utf-8") as out:
                out.write(summary)

            print(f"Saved to: {output_path}")

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
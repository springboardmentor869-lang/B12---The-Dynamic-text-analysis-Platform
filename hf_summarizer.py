import os
import requests
from dotenv import load_dotenv

load_dotenv()

# CONFIG
HF_TOKEN = os.getenv("HF_TOKEN")
print("Loaded token:", os.getenv("HF_TOKEN"))

model = "google/pegasus-xsum"

input_folder = "results/preprocessed"
output_folder = "results/summaries_hf"

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in .env")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


def chunk_text(text, chunk_size=350):

    """Split long text into smaller chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


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

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"HF error {response.status_code}: {response.text}")

    return response.json()[0]["summary_text"]


def summarize_text(text):
    chunks = chunk_text(text)
    summaries = []

    for i, chunk in enumerate(chunks):
        print(f"  Summarizing chunk {i+1}/{len(chunks)}...")
        summary = summarize_chunk(chunk)
        summaries.append(summary)

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
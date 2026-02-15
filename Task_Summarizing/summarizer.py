# summarizer.py
import os
from typing import Optional
from openai import OpenAI  # LM Studio client
import dotenv

dotenv.load_dotenv()


def chunk_text(text: str, chunk_size: int = 800) -> list[str]:
    """
    Split text into smaller chunks (word-based) to avoid overloading GPU.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def summarize_text_with_lm_studio(text_path: str, max_length: int = 1000) -> Optional[str]:
    # Read input
    if not os.path.isfile(text_path):
        return "No text to summarize."

    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()

    if not text.strip():
        return "Text file is empty."

    client = OpenAI(
        base_url="http://localhost:1234/v1",  # LM Studio local API
        api_key="lmstudio"                     # LM Studio local free key
    )

    # Chunking
    chunks = chunk_text(text, chunk_size=800)
    print(f"Total chunks: {len(chunks)}")

    chunk_summaries = []

    for idx, chunk in enumerate(chunks, start=1):
        print(f"Summarizing chunk {idx}/{len(chunks)}...")
        prompt = f"Summarize the following text (Markdown allowed) in {max_length} words or less, focusing on key points:\n\n{chunk}"

        try:
            response = client.chat.completions.create(
                model="qwen/qwen3-4b-2507",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length,
                temperature=0.7
            )
            summary = response.choices[0].message.content.strip()
            chunk_summaries.append(summary)
        except Exception as e:
            chunk_summaries.append(f"Error summarizing chunk {idx}: {str(e)}")

    # Combine all chunk summaries
    final_summary = "\n\n".join(chunk_summaries)
    return final_summary


if __name__ == "__main__":
    input_file = "converted.md"
    summary = summarize_text_with_lm_studio(input_file)

    print("\n===== FINAL SUMMARY =====\n")
    print(summary)

    # Save final summary
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "final_summary.md")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"\n Final summary saved to {output_file}")

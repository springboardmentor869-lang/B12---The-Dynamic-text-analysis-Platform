import ollama
import os

# File to summarize
file_path = "../output_docs_docling/task2pdf_sample.md"

with open(file_path, "r", encoding="utf-8") as f:
    document_text = f.read()

# Limit input size
document_text = document_text[:10000]

prompt = f"""
You are a professional financial analyst.

Generate a structured comprehensive summary of the following financial document.

Include:
1. Executive Summary
2. Financial Performance
3. Risk Factors
4. Future Outlook

Document:
{document_text}
"""

response = ollama.chat(
    model="mistral",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

summary = response["message"]["content"]

os.makedirs("outputs", exist_ok=True)

with open("outputs/summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)

print("✅ Summary generated successfully!\n")
print(summary[:600])

import requests
import os

API_KEY = "YOUR_API_KEY"

with open("input_docs/report.md", "r", encoding="utf-8") as f:
    text = f.read()

prompt = "Summarize this document clearly:\n\n" + text[:12000]

r = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
)

print("STATUS:", r.status_code)
print(r.text)

data = r.json()

summary = data["choices"][0]["message"]["content"]

os.makedirs("output", exist_ok=True)

with open("output/summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)

print("Summary saved to output/summary.txt")

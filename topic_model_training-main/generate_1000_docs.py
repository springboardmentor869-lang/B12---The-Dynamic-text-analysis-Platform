import random
import os

topics = [
    "technology and artificial intelligence",
    "healthcare and medical research",
    "finance and banking systems",
    "space exploration and satellites",
    "sports and international tournaments",
    "climate change and renewable energy",
    "education and universities",
    "cryptocurrency and blockchain",
    "politics and government policies",
    "scientific discoveries and innovation"
]

os.makedirs("data", exist_ok=True)

with open("data/documents.txt", "w", encoding="utf-8") as f:
    for _ in range(1000):
        topic = random.choice(topics)
        sentence = f"This document discusses {topic} and its global impact."
        f.write(sentence + "\n")

print("✅ 1000 documents generated successfully.")
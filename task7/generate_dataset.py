import os
import random
import pandas as pd
from datasets import load_dataset

FINAL_SIZE = 1100


def make_two_paragraph(text1, text2):
    return text1.strip() + "\n\n" + text2.strip()


print("Loading datasets...")

# ---------------------------
# 1️⃣ DBpedia (Highly diverse – 14 categories)
# ---------------------------
dbpedia = load_dataset("dbpedia_14", split="train[:450]")
dbpedia_docs = [
    make_two_paragraph(item["title"], item["content"])
    for item in dbpedia
]

# ---------------------------
# 2️⃣ Yahoo Answers (10 broad domains)
# ---------------------------
yahoo = load_dataset("yahoo_answers_topics", split="train[:450]")
yahoo_docs = [
    make_two_paragraph(item["question_title"], item["best_answer"])
    for item in yahoo
]

# ---------------------------
# 3️⃣ AG News (News-style diversity)
# ---------------------------
ag = load_dataset("ag_news", split="train[:450]")
ag_docs = [
    make_two_paragraph(item["text"], item["text"])
    for item in ag
]

print("Combining documents...")

all_docs = dbpedia_docs + yahoo_docs + ag_docs
random.shuffle(all_docs)

# Trim to exact size
all_docs = all_docs[:FINAL_SIZE]

# Create dataframe
df = pd.DataFrame({
    "id": range(1, len(all_docs) + 1),
    "text": all_docs
})

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Save dataset
dataset_path = os.path.join("data", "dataset.csv")
df.to_csv(dataset_path, index=False)

print(f"Dataset created successfully with {len(df)} documents.")
print(f"Saved at: {dataset_path}")



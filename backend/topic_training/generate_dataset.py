import random
import os

os.makedirs("dataset", exist_ok=True)

file_path = "dataset/documents.txt"

subjects = [
    "Artificial intelligence",
    "Cybersecurity systems",
    "Cloud computing",
    "Machine learning",
    "Blockchain networks",
    "Stock markets",
    "Interest rate policies",
    "Cryptocurrency platforms",
    "Financial institutions",
    "Global inflation trends",
    "Medical research",
    "Vaccination programs",
    "Telemedicine services",
    "Mental health initiatives",
    "Hospital management systems",
    "Climate change policies",
    "Renewable energy markets",
    "Deforestation impacts",
    "Sustainable agriculture practices",
    "Ocean conservation programs",
    "Online education platforms",
    "STEM research programs",
    "University innovation hubs",
    "Scholarship initiatives",
    "Digital learning systems"
]

actions = [
    "are transforming",
    "are influencing",
    "are reshaping",
    "are expanding",
    "are strengthening",
    "are modernizing",
    "are disrupting",
    "are accelerating",
    "are improving",
    "are redefining"
]

objects = [
    "global industry standards.",
    "economic development strategies.",
    "technological advancement efforts.",
    "public policy frameworks.",
    "international collaboration models.",
    "long-term sustainability goals.",
    "digital infrastructure planning.",
    "organizational growth patterns.",
    "market competitiveness dynamics.",
    "innovation ecosystems worldwide."
]

extra = [
    "Experts highlight both opportunities and challenges.",
    "Recent studies indicate significant progress.",
    "Stakeholders emphasize regulatory importance.",
    "Investment levels continue to rise steadily.",
    "Policy reforms are being implemented gradually.",
    "Research findings support long-term growth.",
    "Market conditions remain competitive.",
    "Global collaboration strengthens outcomes.",
    "Technological breakthroughs drive change.",
    "Sustainability remains a priority."
]

documents = set()

while len(documents) < 1000:
    sentence = (
        f"{random.choice(subjects)} "
        f"{random.choice(actions)} "
        f"{random.choice(objects)} "
        f"{random.choice(extra)}"
    )
    documents.add(sentence)

with open(file_path, "w", encoding="utf-8") as f:
    for doc in documents:
        f.write(doc + "\n")

print("✅ 1000 UNIQUE documents generated successfully!")
print("Saved at:", file_path)

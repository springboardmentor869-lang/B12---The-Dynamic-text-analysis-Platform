import random
import os

topics = {
    "technology": [
        "Artificial intelligence is transforming industries worldwide.",
        "Cybersecurity protects systems from digital attacks.",
        "Cloud computing enables scalable infrastructure.",
        "Machine learning models analyze large datasets.",
        "Blockchain ensures secure transactions."
    ],
    "finance": [
        "Stock markets fluctuate based on economic indicators.",
        "Investors diversify portfolios to reduce risk.",
        "Banks provide loans and financial services.",
        "Cryptocurrency adoption is increasing globally.",
        "Inflation impacts purchasing power."
    ],
    "healthcare": [
        "Doctors diagnose diseases using medical imaging.",
        "Vaccines prevent infectious diseases.",
        "Hospitals use advanced surgical equipment.",
        "Medical research improves treatment methods.",
        "Public health policies protect communities."
    ],
    "sports": [
        "Football is one of the most popular sports.",
        "Athletes train rigorously for competitions.",
        "Olympic games unite countries worldwide.",
        "Basketball requires teamwork and strategy.",
        "Cricket tournaments attract large audiences."
    ],
    "space": [
        "Space exploration advances scientific discovery.",
        "Astronauts conduct experiments in orbit.",
        "Rockets launch satellites into space.",
        "Mars missions aim to explore new frontiers.",
        "Telescopes capture distant galaxies."
    ],
    "education": [
        "Universities promote academic excellence.",
        "Students prepare for competitive exams.",
        "Online learning platforms expand access.",
        "Research contributes to innovation.",
        "Teachers inspire lifelong learning."
    ],
    "environment": [
        "Climate change affects global ecosystems.",
        "Renewable energy reduces carbon emissions.",
        "Forests play a vital role in biodiversity.",
        "Recycling minimizes environmental waste.",
        "Sustainable development protects resources."
    ],
    "politics": [
        "Elections determine government leadership.",
        "Policies influence economic growth.",
        "Diplomatic relations shape global stability.",
        "Legislation affects public welfare.",
        "Democracy promotes citizen participation."
    ]
}

documents = []

while len(documents) < 1000:
    category = random.choice(list(topics.keys()))
    sentence = random.choice(topics[category])
    variation = f" This development significantly impacts {category} sector growth."
    documents.append(sentence + variation)

os.makedirs("data", exist_ok=True)

with open("data/documents.txt", "w", encoding="utf-8") as f:
    for doc in documents:
        f.write(doc + "\n")

print("✅ 1000 documents generated successfully.")
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
from groq import Groq

import nltk
from transformers import pipeline

from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
import numpy as np
import pickle

# -----------------------------
# 🔧 INITIAL SETUP
# -----------------------------
app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Download nltk
nltk.download("punkt", quiet=True)

# -----------------------------
# 💬 SENTIMENT MODEL
# -----------------------------
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert",
    tokenizer="ProsusAI/finbert"
)

# -----------------------------
# 📊 LOAD TOPIC MODEL
# -----------------------------
topic_model = None
centroids = None

try:
    topic_model = BERTopic.load("models/bertopic_model")
    with open("models/centroids.pkl", "rb") as f:
        centroids = pickle.load(f)
    print("✅ BERTopic model loaded")
except:
    print("⚠ Topic model not found")

# -----------------------------
# 📄 PDF → TEXT
# -----------------------------
def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    return "".join([page.get_text() for page in doc])

# -----------------------------
# 🤖 SUMMARIZATION
# -----------------------------
def summarize_text(text):
    try:
        prompt = f"""
        Give:
        1. Executive Summary
        2. Key Takeaways

        Text:
        {text[:5000]}
        """

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        # ✅ Safe extraction
        if completion and completion.choices:
            return completion.choices[0].message.content
        else:
            return "No response from Groq API"

    except Exception as e:
        print("❌ ERROR:", str(e))   # print in terminal
        return f"Error: {str(e)}"

# -----------------------------
# 💬 SENTIMENT FUNCTIONS
# -----------------------------
def split_sentences(text):
    return nltk.sent_tokenize(text)

def analyze_sentiment(sentences):
    results = []

    for sent in sentences:
        if len(sent) < 10:
            continue

        res = sentiment_pipeline(sent)[0]

        results.append({
            "sentence": sent,
            "label": res["label"].lower(),  # normalize
            "score": round(res["score"] * 100, 2)
        })

    return results

def sentiment_summary(results):
    return {
        "total": len(results),
        "positive": sum(1 for r in results if r["label"] == "positive"),
        "negative": sum(1 for r in results if r["label"] == "negative"),
        "neutral": sum(1 for r in results if r["label"] == "neutral")
    }

# -----------------------------
# 📊 TOPIC MODELING
# -----------------------------
def get_topic_distribution(text):
    if not topic_model or not centroids:
        return {"error": "Topic model not available"}

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    emb = embedding_model.encode([text])[0]

    scores = []

    # 🔹 Calculate similarity for all topics
    for topic_id, data in centroids.items():
        centroid = np.array(data["centroid"])

        score = np.dot(emb, centroid) / (
            np.linalg.norm(emb) * np.linalg.norm(centroid)
        )

        scores.append({
            "topic": data["label"],
            "score": score
        })

    # 🔹 Normalize scores → percentage
    total = sum(s["score"] for s in scores if s["score"] > 0)

    for s in scores:
        if total > 0:
            s["percentage"] = round((s["score"] / total) * 100, 2)
        else:
            s["percentage"] = 0

    # 🔹 Sort & take top 5
    scores = sorted(scores, key=lambda x: x["percentage"], reverse=True)[:5]

    return scores

# -----------------------------
# 🚀 API: SUMMARY
# -----------------------------
@app.post("/summary/")
async def get_summary(file: UploadFile = File(...)):
    try:
        file_path = file.filename

        with open(file_path, "wb") as f:
            f.write(await file.read())

        text = extract_text(file_path)

        if not text.strip():
            return {"error": "Empty PDF"}

        summary = summarize_text(text)

        return {"summary": summary}

    except Exception as e:
        print("❌ Summary API Error:", str(e))
        return {"error": str(e)}

# -----------------------------
# 🚀 API: SENTIMENT (FIXED 🔥)
# -----------------------------
@app.post("/sentiment/")
async def get_sentiment(file: UploadFile = File(...)):
    file_path = file.filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)

    sentences = split_sentences(text)
    sentiment_results = analyze_sentiment(sentences)
    sentiment_stats = sentiment_summary(sentiment_results)

    # ✅ Group sentences
    grouped = {
        "positive": [],
        "negative": [],
        "neutral": []
    }

    for r in sentiment_results:
        label = r["label"]

        if label in grouped:
            grouped[label].append({
                "text": r["sentence"],
                "score": r["score"]
            })

    return {
        "sentiment_summary": sentiment_stats,
        "sample_sentiments": {
    "positive": grouped["positive"],
    "negative": grouped["negative"],
    "neutral": grouped["neutral"]
}
    }

# -----------------------------
# 🚀 API: TOPIC
# -----------------------------
# -----------------------------
# 🚀 API: TOPIC
# -----------------------------
@app.post("/topic/")
async def get_topic_api(file: UploadFile = File(...)):
    try:
        file_path = file.filename

        with open(file_path, "wb") as f:
            f.write(await file.read())

        text = extract_text(file_path)

        topics = get_topic_distribution(text)

        return {"topics": topics}

    except Exception as e:
        print("❌ Topic API Error:", str(e))
        return {"error": str(e)}
# -----------------------------
# 🚀 API: EXTRACT TEXT
# -----------------------------
@app.post("/extract-text/")
async def extract_text_api(file: UploadFile = File(...)):
    file_path = file.filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)

    if not text.strip():
        return {"error": "Empty PDF"}

    return {"text": text[:5000]}  # limit for UI
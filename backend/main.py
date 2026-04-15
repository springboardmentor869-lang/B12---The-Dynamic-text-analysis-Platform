from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
import google.generativeai as genai

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

# ✅ CORS (IMPORTANT for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyCIldb8bDvNIIrMDXUyYsmJ3rAZqpX50Ic"))

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
    print("Loading BERTopic model...")

    topic_model = BERTopic.load("./models/bertopic_model")

    with open("./models/centroids.pkl", "rb") as f:
        centroids = pickle.load(f)

    print("✅ BERTopic model loaded successfully")

except Exception as e:
    print("❌ BERTopic loading error:")
    print(e)

# -----------------------------
# 📄 PDF → TEXT
# -----------------------------
def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    return "".join([page.get_text() for page in doc])

# -----------------------------
# 📝 PDF → MARKDOWN
# -----------------------------
def pdf_to_markdown(text):
    return text + "\n\n"

# -----------------------------
# 🤖 SUMMARIZATION
# -----------------------------
def summarize_text(text):
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Give:
    1. Executive Summary
    2. Key Takeaways

    Text:
    {text[:10000]}
    """

    response = model.generate_content(prompt)
    return response.text

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
            "label": res["label"],
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
def get_topic(text):
    if not topic_model or not centroids:
        return "Topic model not available"

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    emb = embedding_model.encode([text])[0]

    best_topic = None
    best_score = -1

    for topic_id, data in centroids.items():
        centroid = np.array(data["centroid"])

        score = np.dot(emb, centroid) / (
            np.linalg.norm(emb) * np.linalg.norm(centroid)
        )

        if score > best_score:
            best_score = score
            best_topic = data["label"]

    return best_topic

# -----------------------------
# 🚀 API: SUMMARY
# -----------------------------
@app.post("/summary/")
async def get_summary(file: UploadFile = File(...)):
    file_path = file.filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)

    if not text.strip():
        return {"error": "Empty PDF"}

    summary = summarize_text(text)

    return {"summary": summary}

# -----------------------------
# 🚀 API: SENTIMENT
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

    return {
        "sentiment_summary": sentiment_stats,
        "sample_sentiments": sentiment_results[:5]
    }

# -----------------------------
# 🚀 API: TOPIC
# -----------------------------
@app.post("/topic/")
async def get_topic_api(file: UploadFile = File(...)):
    file_path = file.filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)
    topic = get_topic(text)

    return {"topic": topic}

# -----------------------------
# 🚀 API: MARKDOWN (OPTIONAL)
# -----------------------------
@app.post("/markdown/")
async def get_markdown(file: UploadFile = File(...)):
    file_path = file.filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)
    markdown = pdf_to_markdown(text)

    return {"markdown": markdown[:1000]}
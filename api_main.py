"""
main.py - FastAPI application entry point.

Provides:
- Initializes FastAPI application
- Configures CORS (Cross-Origin Resource Sharing)
- Registers all API routes (convert, sentiment, summarize, classify)

API Modules Included:
- api_convert.py    - Document to Markdown conversion
- api_sentiment.py  - Sentiment analysis
- api_summarize.py  - Document summarization
- api_inference.py  - Topic classification

Features:
- Modular router-based architecture
- Supports frontend-backend communication via CORS
- Centralized API management

Requires:
- fastapi - API framework
- fastapi.middleware.cors - Enable cross-origin requests

Run:
    uvicorn main:app --reload

Access API Docs:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers from different modules
from api_convert import router as convert_router
from api_sentiment import router as sentiment_router
from api_summarize import router as summarizer_router
from api_inference import router as inference_router

app = FastAPI()

# Enable CORS (Frontend - Backend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(convert_router)
app.include_router(sentiment_router)
app.include_router(summarizer_router)
app.include_router(inference_router)
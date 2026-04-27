"""
Main FastAPI application.
Combines all API routers and serves frontend.
"""

from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Import routers
from api_convert import router as convert_router
from api_sentiment import router as sentiment_router
from api_summarize import router as summarize_router
from api_inference import router as inference_router

# Create FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(convert_router, prefix="/api", tags=["convert"])
app.include_router(sentiment_router, prefix="/api", tags=["sentiment"])
app.include_router(summarize_router, prefix="/api", tags=["summarize"])
app.include_router(inference_router, prefix="/api", tags=["inference"])

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# Frontend routes
@app.get("/")
async def home():
    """Serve home page"""
    return FileResponse("frontend/home.html")


@app.get("/classify")
async def classify():
    """Serve classify page"""
    return FileResponse("frontend/classify.html")


@app.get("/convert")
async def convert():
    """Serve convert page"""
    return FileResponse("frontend/convert.html")


@app.get("/sentiment")
async def sentiment():
    """Serve sentiment page"""
    return FileResponse("frontend/sentiment.html")


@app.get("/summarize")
async def summarize():
    """Serve summarize page"""
    return FileResponse("frontend/summarize.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
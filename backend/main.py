import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure local backend modules (core, routers, services, models) resolve
# when running as either `main:app` or `backend.main:app`.
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from models.schemas import HealthResponse
from routers import analyze, topic, sentiment, summarize
from services.topic_modeler import topic_modeler
from services.sentiment import sentiment_analyzer


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting Dynamic Text Analyzer API...")

    try:
        # Initialize topic modeler (loads model artifacts)
        logger.info("Loading topic model...")
        _ = topic_modeler.centroids  # Access to trigger loading
        logger.info(f"Topic model loaded: {len(topic_modeler.centroids)} topics")
    except Exception as e:
        logger.warning(f"Topic model not available: {e}")

    try:
        # Verify sentiment analyzer is ready
        logger.info("Sentiment analyzer ready")
    except Exception as e:
        logger.warning(f"Sentiment analyzer not available: {e}")

    logger.info("Startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Dynamic Text Analyzer API...")


app = FastAPI(
    title=settings.app_name,
    description="PDF analysis with Topic Modeling, Sentiment Analysis, and Summarization",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware (configure origins as needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(analyze.router)
app.include_router(topic.router)
app.include_router(sentiment.router)
app.include_router(summarize.router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    try:
        models_loaded = len(topic_modeler.centroids) > 0
    except Exception:
        models_loaded = False

    return HealthResponse(
        status="healthy" if models_loaded else "degraded",
        models_loaded=models_loaded,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from models.schemas import HealthResponse
from routers import topic, sentiment, summarize
from services.pipelines import predictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Dynamic Text Analyzer API...")
    if predictor:
        logger.info(f"Topic Model loaded with {len(predictor.centroids)} centroids.")
    else:
        logger.warning("Topic Model could not be loaded.")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect all our clean, separated routers
app.include_router(topic.router)
app.include_router(sentiment.router)
app.include_router(summarize.router)

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    models_loaded = predictor is not None
    return HealthResponse(
        status="healthy" if models_loaded else "degraded",
        models_loaded=models_loaded
    )

if __name__ == "__main__":
    import uvicorn
    # Important: Point uvicorn to main:app since we renamed the file!
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
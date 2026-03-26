from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# Topic Modeling Schemas
class DominantTopic(BaseModel):
    topic_id: int
    label: str
    avg_similarity_score: float
    chunks_matched: int
    total_chunks: int


class TopicFound(BaseModel):
    topic_id: int
    label: str
    chunks_matched: int
    avg_score: float


class ChunkDetail(BaseModel):
    chunk_id: int
    preview: str
    topic_id: int
    label: str
    score: float
    keywords: list[str] = []


class TopicModelingResult(BaseModel):
    dominant_topic: DominantTopic
    all_topics_found: list[TopicFound]
    chunk_details: list[ChunkDetail] = []


# Sentiment Analysis Schemas
class SentenceSentiment(BaseModel):
    sentence: str
    label: str
    score: float
    chunked: bool = False


class SentimentSummary(BaseModel):
    positive: float
    negative: float
    neutral: float


class SentimentResult(BaseModel):
    overall_sentiment: str
    summary: SentimentSummary
    per_sentence: list[SentenceSentiment]


# Summarization Schemas
class SummarizationResult(BaseModel):
    summary: str
    word_count: int


# Analysis Results Container
class AnalysisResults(BaseModel):
    file_name: str
    topic_modeling: TopicModelingResult
    sentiment_analysis: SentimentResult
    summarization: SummarizationResult
    processing_time_seconds: float


# Task Response Schemas
class AnalyzeSubmitResponse(BaseModel):
    task_id: str
    status: str
    message: str


class AnalyzeStatusResponse(BaseModel):
    task_id: str
    status: str
    results: Optional[AnalysisResults] = None
    error: Optional[str] = None
    processing_time_seconds: Optional[float] = None


# Individual Endpoint Schemas
class TopicModelResponse(BaseModel):
    dominant_topic: DominantTopic
    all_topics_found: list[TopicFound]
    chunk_details: list[ChunkDetail] = []


class SentimentResponse(BaseModel):
    overall_sentiment: str
    per_sentence: list[SentenceSentiment]


class SummarizeResponse(BaseModel):
    summary: str
    word_count: int


# Health Check
class HealthResponse(BaseModel):
    status: str
    models_loaded: bool

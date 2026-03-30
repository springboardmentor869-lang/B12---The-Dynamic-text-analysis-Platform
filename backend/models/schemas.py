from pydantic import BaseModel
from typing import List, Optional

class HealthResponse(BaseModel):
    status: str
    models_loaded: bool

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
    keywords: List[str]

class TopicModelResponse(BaseModel):
    dominant_topic: DominantTopic
    all_topics_found: List[TopicFound]
    chunk_details: List[ChunkDetail]

class SentenceSentiment(BaseModel):
    sentence: str
    label: str
    score: float
    chunked: Optional[bool] = False

class SentimentResponse(BaseModel):
    overall_sentiment: str
    per_sentence: List[SentenceSentiment]

class SummarizeResponse(BaseModel):
    summary: str
    word_count: int

class AnalyzeSubmitResponse(BaseModel):
    task_id: str
    status: str
    message: str

class AnalysisResults(BaseModel):
    file_name: str
    topic_modeling: TopicModelResponse
    sentiment_analysis: SentimentResponse
    summarization: SummarizeResponse
    processing_time_seconds: float

class AnalyzeStatusResponse(BaseModel):
    task_id: str
    status: str
    results: Optional[AnalysisResults] = None
    error: Optional[str] = None
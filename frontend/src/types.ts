// src/types.ts

export interface DominantTopic {
  topic_id: number;
  label: string;
  avg_similarity_score: number;
  chunks_matched: number;
  total_chunks: number;
}

export interface TopicFound {
  topic_id: number;
  label: string;
  chunks_matched: number;
  avg_score: number;
}

export interface ChunkDetail {
  chunk_id: number;
  preview: string;
  topic_id: number;
  label: string;
  score: number;
  keywords: string[];
}

export interface TopicModelResponse {
  dominant_topic: DominantTopic;
  all_topics_found: TopicFound[];
  chunk_details: ChunkDetail[];
}

export interface SentenceSentiment {
  sentence: string;
  label: string;
  score: number;
  chunked?: boolean;
}

export interface SentimentResponse {
  overall_sentiment: string;
  per_sentence: SentenceSentiment[];
}

export interface SummarizeResponse {
  summary: string;
  word_count: number;
}

export interface AnalysisResults {
  file_name: string;
  topic_modeling: TopicModelResponse;
  sentiment_analysis: SentimentResponse;
  summarization: SummarizeResponse;
  processing_time_seconds: number;
}

export interface ReportData {
  type: 'full' | 'topic-model' | 'sentiment' | 'summarize';
  filename: string;
  data: AnalysisResults | TopicModelResponse | SentimentResponse | SummarizeResponse;
}
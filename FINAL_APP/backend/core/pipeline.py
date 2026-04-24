import asyncio
import traceback
from services.parsing.parser import parse_document
from services.summarization.summ import summarize
from services.sentiment.sent import analyze_sentiment
from services.topic_modeling.clustering import extract_topics
from utils.chunking import chunk_text


async def run_pipeline(content, filename, mode, task_id, task_manager):
    try:
        # Step 1: Extract text
        task_manager.update_progress(task_id, f"Parsing {filename}...", 5)
        text, _ = await parse_document(content, filename)

        result = {}

        if mode == "summary":
            chunks = chunk_text(text, max_words=200)
            result["summary"] = await asyncio.to_thread(summarize, text, task_manager, task_id)

        elif mode == "sentiment":
            result["sentiment"] = await asyncio.to_thread(analyze_sentiment, text, task_manager, task_id)

        elif mode == "topics":
            chunks = chunk_text(text, max_words=200)
            result["topics"] = await asyncio.to_thread(extract_topics, chunks, task_manager, task_id)

        elif mode == "full":
            chunks = chunk_text(text, max_words=200)
            task_manager.update_progress(task_id, "Running full analysis...", 10)
            
            # Run sequentially to prevent overloading local Ollama/GPU resources
            summary_res = await asyncio.to_thread(summarize, text, task_manager, task_id)
            sentiment_res = await asyncio.to_thread(analyze_sentiment, text, task_manager, task_id)
            topics_res = await asyncio.to_thread(extract_topics, chunks, task_manager, task_id)
            
            result["summary"] = summary_res
            result["sentiment"] = sentiment_res
            result["topics"] = topics_res

        # Step 4: Save result
        task_manager.update_task(task_id, result)
    except Exception as e:
        print(f"PIPELINE ERROR: {e}")
        traceback.print_exc()
        task_manager.fail_task(task_id, str(e))
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. SETUP & CONFIGURATION ---
# load_dotenv() pulls your API keys from a hidden .env file for security.
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY") or "PASTE_YOUR_KEY_HERE"

# OpenRouter acts as an 'Aggregator' - one API that gives you access to 
# many different 'Brain' models (Gemini, Llama, GPT-4, etc.)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Financial Summarizer", 
    }
)

def _call_openrouter_with_retry(model, messages, max_retries=3):
    """
    NLP Engineering: Resilience Logic.
    API-based NLP often hits '429 Rate Limits'. This function implements 
    'Exponential Backoff' to wait longer between each failed attempt.
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3 # Low temperature = Higher accuracy/Less 'hallucination'
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Backoff: 1s, 2s, 4s
                print(f"Rate limit hit (429). Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise e

def summarize_document(file_path):
    """
    NLP Phase: File-to-Summary Pipeline.
    Reads a physical file, constructs a structured prompt, and generates a bulleted summary.
    """
    if not os.path.exists(file_path):
        print(f"Error: Could not find file at {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    print(f"--- Document loaded ({len(full_text)} characters) ---")
    
    # 2026 Recommended Model: Gemini 2.0 Flash (Fast, Cheap, and handles 1M tokens)
    model_id = "google/gemini-2.0-flash-001" 

    print(f"Requesting summary from {model_id}...")
    
    # --- PROMPT ENGINEERING ---
    # This acts as the 'Instructions' for the AI. Clarity here is 90% of the work.
    user_prompt = f"""
    You are an Expert Research Assistant and Technical Writer.
    
    TASK:
    Summarize the following document.
    Your summary must be comprehensive, capturing all key details, dates, names, and technical concepts.
    
    GUIDELINES:
    1. **Identify the Type**: adaptability is key. Focus on specs/logic for tech, and facts/events for narratives.
    2. **No Fluff**: Strictly avoid meta-talk like 'The author says...'. State facts directly.
    3. **Structure**: Use bullet points for high scannability in the dashboard.
    
    OUTPUT FORMAT:
    * **Section Overview**: 1-sentence header.
    * **Key Details & Insights**: High-density bullet points.
    * **Critical Data/Quotes**: Extract numbers, formulas, or verbatim quotes.
    
    TEXT CONTENT TO SUMMARIZE:
    {full_text}
    """
    try:
        return _call_openrouter_with_retry(
            model=model_id,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Universal Research Assistant. Your goal is to provide accurate, neutral summaries that adapt to the document's domain. Always prioritize factual data over generalities."
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ]
        )

    except Exception as e:
        # Graceful Degradation: If our specific model is down, try the generic router
        if "404" in str(e):
            print("Specific model ID not found. Trying fallback: openrouter/free...")
            try:
                return _call_openrouter_with_retry(
                    model="openrouter/free",
                    messages=[{"role": "user", "content": f"Summarize this:\n\n{full_text}"}]
                )
            except Exception as e2:
                return f"Critical Error: {e2}"
        return f"Unexpected Error: {e}"

def summarize_text(text: str) -> str:
    """
    NLP Phase: Abstractive Narrative Generation.
    Instead of bullets, this creates a cohesive 'Story' summary using paragraphs.
    Useful for detailed reports where flow matters more than scannability.
    """
    print(f"--- Text loaded ({len(text)} characters) ---")
    
    model_id = "google/gemini-2.0-flash-001"
    
    user_prompt = f"""
    You are an Expert Research Assistant and Technical Writer.
    
    TASK:
    Summarize the following document in a clear, cohesive narrative format using paragraphs.
    
    GUIDELINES:
    1. **Format Requirements**: Write in continuous prose. Strictly DO NOT use bullet points.
    2. **Structure**: 
       - Paragraph 1: Executive Summary.
       - Paragraph 2-3: Integrated details and data.
       - Paragraph 4: Conclusion/Outlook.
    
    TEXT CONTENT TO SUMMARIZE:
    {text}
    """
    
    try:
        return _call_openrouter_with_retry(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a Universal Research Assistant. Your goal is to provide accurate, neutral summaries that adapt to the document's domain (e.g., Technical, Financial, Narrative, or Legal). Always prioritize factual data over generalities."},
                {"role": "user", "content": user_prompt}
            ]
        )
    except Exception as e:
        # Standard Fallback Logic
        if "404" in str(e):
            print("Specific model ID not found. Trying fallback: openrouter/free...")
            try:
                return _call_openrouter_with_retry(
                    model="openrouter/free",
                    messages=[{"role": "user", "content": f"Summarize this:\n\n{text}"}]
                )
            except Exception as e2:
                return f"Critical Error: {e2}"
        return f"Unexpected Error: {e}"

if __name__ == "__main__":
    # --- EXECUTION ---
    target_file = r"..\processed_data\financial_doc.md"
    summary = summarize_document(target_file)
    
    if summary:
        with open("financial_summary_openrouter.md", "w", encoding="utf-8") as f:
            f.write(summary)
        print("\nSUMMARY GENERATED AND SAVED TO: financial_summary_openrouter.md")
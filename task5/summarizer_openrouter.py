import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# 1. SETUP
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY") or "PASTE_YOUR_KEY_HERE"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Financial Summarizer", 
    }
)

def _call_openrouter_with_retry(model, messages, max_retries=3):
    """Call OpenRouter with retry logic for rate limits."""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"Rate limit hit (429). Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise e

def summarize_document(file_path):
    if not os.path.exists(file_path):
        print(f"Error: Could not find file at {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    print(f"--- Document loaded ({len(full_text)} characters) ---")
    
    # 2026 ACTIVE FREE MODELS:
    # 'google/gemini-2.0-flash-001:free' (Updated stable free version)
    # 'meta-llama/llama-3.3-70b-instruct:free' (Excellent for logic)
    # 'openrouter/free' (Auto-picks best available)
    model_id = "google/gemini-2.0-flash-001" 

    print(f"Requesting summary from {model_id}...")
    user_prompt = f"""
    You are an Expert Research Assistant and Technical Writer.
    
    TASK:
    Summarize the following document.
    Your summary must be comprehensive, capturing all key details, dates, names, and technical concepts.
    
    GUIDELINES:
    1. **Identify the Type**: adaptability is key. If it's technical, focus on specs/logic. If narrative, focus on plot/events.
    2. **No Fluff**: Do not use phrases like "The text mentions..." or "The author discusses...". Just state the facts directly.
    3. **Structure**: Use bullet points for readability.
    
    OUTPUT FORMAT:
    * **Section Overview**: A 1-sentence header of what this section covers.
    * **Key Details & Insights**: Detailed bullet points of the most important information.
    * **Critical Data/Quotes**: Extract specific numbers, formulas, or key quotes if present.
    
    TEXT CONTENT TO SUMMARIZE:
    {full_text}
    """
    try:
        return _call_openrouter_with_retry(
            model=model_id,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Financial Analyst. Provide a comprehensive summary including all specific numbers, KPIs, and revenue figures. Use bullet points."
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ]
        )

    except Exception as e:
        # Fallback to the general free router if the specific Gemini ID fails
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
    """Summarize text directly without reading from file."""
    print(f"--- Text loaded ({len(text)} characters) ---")
    
    model_id = "google/gemini-2.0-flash-001"
    
    print(f"Requesting summary from {model_id}...")
    user_prompt = f"""
    You are an Expert Research Assistant and Technical Writer.
    
    TASK:
    Summarize the following document in a clear, cohesive narrative format using paragraphs.
    Your summary must be comprehensive, capturing all key details, dates, names, and technical concepts.
    
    GUIDELINES:
    1. **Format Requirements**: Write in continuous prose using well-structured paragraphs. Strictly DO NOT use bullet points, numbered lists, or fragmented sentences.
    2. **Structure**: 
       - Paragraph 1: Executive Summary & Overview.
       - Paragraph 2-3: Key Details, Insights, and Critical Data/Quotes integrated into the text.
       - Paragraph 4: Conclusion or forward-looking outlook.
    3. **Tone**: Professional, direct, and factual. No fluff.
    
    TEXT CONTENT TO SUMMARIZE:
    {text}
    """
    
    try:
        return _call_openrouter_with_retry(
            model=model_id,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Financial Analyst. Provide a comprehensive summary including all specific numbers, KPIs, and revenue figures. Use bullet points."
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ]
        )
    except Exception as e:
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
    target_file = r"..\processed_data\financial_doc.md"
    summary = summarize_document(target_file)
    
    if summary:
        with open("financial_summary_openrouter.md", "w", encoding="utf-8") as f:
            f.write(summary)
        print("\nSUMMARY GENERATED AND SAVED TO: financial_summary_openrouter.md")
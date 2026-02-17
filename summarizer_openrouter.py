import os
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
        response = client.chat.completions.create(
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
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

    except Exception as e:
        # Fallback to the general free router if the specific Gemini ID fails
        if "404" in str(e):
            print("Specific model ID not found. Trying fallback: openrouter/free...")
            try:
                response = client.chat.completions.create(
                    model="openrouter/free",
                    messages=[{"role": "user", "content": f"Summarize this:\n\n{full_text}"}]
                )
                return response.choices[0].message.content
            except Exception as e2:
                return f"Critical Error: {e2}"
        return f"Unexpected Error: {e}"

if __name__ == "__main__":
    target_file = r"processed_data\financial doc.md"
    summary = summarize_document(target_file)
    
    if summary:
        with open("financial_summary_openrouter.md", "w", encoding="utf-8") as f:
            f.write(summary)
        print("\nSUMMARY GENERATED AND SAVED TO: financial_summary_openrouter.md")
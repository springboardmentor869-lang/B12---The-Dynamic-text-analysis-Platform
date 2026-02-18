import os
import json
import time
import nltk #semantic analysis
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed #multitasking engine


load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    default_headers={"HTTP-Referer": "http://localhost:3000", "X-Title": "Sentiment Analysis"}
)

def analyze_sentiment_batch(sentences, batch_index, total_batches):
    formatted_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])

    prompt = f"""
    TASK: Analyze sentiment. Return ONLY raw JSON.
    INPUT:
    {formatted_text}

    OUTPUT FORMAT:
    [
      {{"sentence_snippet": "First 5 words...", "sentiment": "Positive", "confidence": 0.9}}
    ]
    """

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="openrouter/free",
                messages=[
                    {"role": "system", "content": "You are a JSON-only Sentiment Engine."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            content = response.choices[0].message.content

            if "```" in content:
                content = content.split("```")[-2]
                if content.startswith("json"): content = content[4:]
            
            content = content.strip()
            data = json.loads(content)
            if isinstance(data, list):
                return data
                
        except Exception as e:
            time.sleep(2)
    
    print(f"      ❌ Batch {batch_index} failed.")
    return []

def main(file_path):
    # Dynamic Path Handling
    if not os.path.exists(file_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir) 
        possible_paths = [
            os.path.join(project_root, "processed_data", "financial doc.md"),
            os.path.join(project_root, "processed_data", "financial_doc.md")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if not os.path.exists(file_path):
            print(f"Error: File not found. Checked: {possible_paths}")
            return

    print(f"1. Reading: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    all_sentences = nltk.sent_tokenize(full_text)
    all_sentences = [s for s in all_sentences if len(s) > 20]
    
    print(f"   -> Found {len(all_sentences)} valid sentences.")

    # 2. Parallel Processing
    BATCH_SIZE = 20 
    batches = [all_sentences[i:i + BATCH_SIZE] for i in range(0, len(all_sentences), BATCH_SIZE)]
    
    print(f"2. Analyzing {len(batches)} batches in PARALLEL...")
    results = []

    def process_wrapper(args):
        b, idx, tot = args
        return analyze_sentiment_batch(b, idx, tot)

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_wrapper, (b, i+1, len(batches))) for i, b in enumerate(batches)]
        for future in as_completed(futures):
            res = future.result()
            results.extend(res)
            print(f"   ✓ Batch finished ({len(res)} items)")

    # 3. Statistics 
    print("\n3. Calculating Statistics...")
    
    stats = {"Positive": 0, "Negative": 0, "Neutral": 0}
    total_confidence = 0
    valid_count = 0
    
    for item in results:
        if not isinstance(item, dict):
            continue 
        
        sent = item.get("sentiment", "Neutral").capitalize()
        if "Pos" in sent: sent = "Positive"
        elif "Neg" in sent: sent = "Negative"
        else: sent = "Neutral"
        
        if sent in stats: stats[sent] += 1
        else: stats["Neutral"] += 1
            
        total_confidence += item.get("confidence", 0)
        valid_count += 1

    avg_confidence = total_confidence / valid_count if valid_count > 0 else 0

    if valid_count > 0:
        overall_score = (stats["Positive"] - stats["Negative"]) / valid_count
    else:
        overall_score = 0

    if overall_score > 0.15: overall_label = "POSITIVE"
    elif overall_score < -0.15: overall_label = "NEGATIVE"
    else: overall_label = "NEUTRAL"

    # 4. Output Report
    report = f"""
### SENTIMENT ANALYSIS REPORT
**File:** {file_path}
**Sentences Analyzed:** {valid_count}

#### EXECUTIVE SUMMARY
* **Overall Sentiment:** {overall_label}
* **Sentiment Score:** {overall_score:.2f} (Scale: -1.0 to +1.0)
* **Avg Confidence:** {avg_confidence:.2%}

#### BREAKDOWN
* **Positive:** {stats['Positive']}
* **Negative:** {stats['Negative']}
* **Neutral:** {stats['Neutral']}
"""
    output_file = "sentiment_report.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n" + "="*40)
    print(f" ANALYSIS COMPLETE: {overall_label}")
    print(f" Positive: {stats['Positive']} | Negative: {stats['Negative']} | Neutral: {stats['Neutral']}")
    print(f" Saved report to '{output_file}'")
    print("="*40)
    print(f" FINAL REPORT SUMMARY:")
    print(f" -> Overall Sentiment: {overall_label}")
    print(f" -> Sentiment Score:   {overall_score:.2f} (Scale: -1 to +1)")
    print(f" -> Avg. Confidence:   {avg_confidence:.1%}")
    print("=" * 40)

if __name__ == "__main__":
    main(r"..\processed_data\financial_doc.md")
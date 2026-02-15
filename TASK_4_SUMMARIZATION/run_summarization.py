import os
from src.summarizer import DocumentSummarizer

INPUT_DIR = "data"
OUTPUT_DIR = "output"

def run_task_4():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # Initialize the AI
    ai_model = DocumentSummarizer()
    
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".txt"):
            print(f"\nSummarizing: {filename}...")
            
            with open(os.path.join(INPUT_DIR, filename), "r", encoding="utf-8") as f:
                content = f.read()
            
            # Generate Summary
            summary_result = ai_model.summarize(content)
            
            # Save Summary
            output_path = os.path.join(OUTPUT_DIR, f"summary_{filename}")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary_result)
            
            print(f"Summary Saved: {output_path}")
            print("-" * 30)
            print(f"AI SUMMARY: {summary_result}")

if __name__ == "__main__":
    run_task_4()
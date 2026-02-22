"""
summarizer.py - Google Gemini-based structured document summarizer.
This script:
    - Reads extracted text files from results/extracted/
    - Sends document content to Google Gemini API
    - Generates structured summaries
    - Saves summaries as Markdown files in results/summaries/

Model Used:
- gemini-2.0-flash → Fast and efficient large language model

Summary Structure:
-
1. Executive Summary
2. Key Concepts
3. Technical Highlights
4. Important Insights
5. Conclusion

Required Libraries:
- os            : File and directory operations
- dotenv        : Load environment variables from .env
- google.genai  : Gemini API client library

Environment Requirements:
- A .env file containing:
      GEMINI_API_KEY=your_google_gemini_api_key

Input:
- Text files (.txt) inside:
      results/extracted/<parser_name>/

Output:
- Structured Markdown summaries saved to:
      results/summaries/<parser_name>/
"""

import os
from google import genai
from dotenv import load_dotenv


# Configuration
extracted_root = "results/extracted"
summary_root = "results/summaries"
model_name = "gemini-2.0-flash" 


# Loading API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)


# Summarization function
def summarize_text(text: str) -> str:
    
    prompt = f"""
You are an expert documentation analyst.

Provide a structured and comprehensive summary of the document below.

Structure:
1. Executive Summary
2. Key Concepts
3. Technical Highlights
4. Important Insights
5. Conclusion

DOCUMENT:
{text}
"""

    # Send request to Gemini model
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    return response.text


# Processing extracted files and generate summaries
def main():
    
    if not os.path.exists(extracted_root):
        print("Extracted folder not found.")
        return

    # Iterate over parser subfolders
    for parser_folder in os.listdir(extracted_root):
        parser_path = os.path.join(extracted_root, parser_folder)

        if not os.path.isdir(parser_path):
            continue

        print(f"\nProcessing parser: {parser_folder}")

        summary_parser_path = os.path.join(summary_root, parser_folder)
        os.makedirs(summary_parser_path, exist_ok=True)

        for filename in os.listdir(parser_path):
            if not filename.endswith(".txt"):
                continue

            input_path = os.path.join(parser_path, filename)

            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()

            print(f"  Summarizing: {filename}")

            try:
                summary = summarize_text(text)

                output_filename = filename.replace(".txt", "_summary.md")
                output_path = os.path.join(summary_parser_path, output_filename)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(summary)

                print(f"  Saved summary to: {output_path}")

            except Exception as e:
                print(f"  Error processing {filename}: {e}")


if __name__ == "__main__":
    main()
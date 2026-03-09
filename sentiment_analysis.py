"""
sentiment_analysis.py - sentence and document-level sentiment analysis utility.

Description:
This module performs sentence-level sentiment analysis on extracted text files
and computes an overall document sentiment using weighted average confidence.

CLI: python sentiment_analysis.py

Model Used:
- cardiffnlp/twitter-roberta-base-sentiment (Hugging Face Transformer)

Libraries Used:
- transformers      : Hugging Face pipeline for sentiment analysis
- torch             : Backend for transformer model
- huggingface-hub   : Optional authentication for model access
- huggingface_hub   : Authenticate using Hugging Face token
- python-dotenv     : Load environment variables
- os                : File and directory handling
- re                : Sentence splitting
- dotenv            : Load environment variables

Environment Variable Required (Optional but Recommended):
- HF_TOKEN : Hugging Face access token

Input:
- results/extracted/<parser_name>/*.txt

Output:
- results/sentiment/<parser_name>/*_sentiment.txt
"""

import os
import re
from transformers import pipeline
from dotenv import load_dotenv
from huggingface_hub import login

load_dotenv()

hf_token = os.getenv("HF_TOKEN")
if hf_token:
    login(hf_token)


# Load sentiment pipeline
sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment",
    return_all_scores=False
)

input_folder = "results/extracted"
output_folder = "results/sentiment"

os.makedirs(output_folder, exist_ok=True)

# Splits text into sentences using a simple regex rule
def split_sentences(text):
    # Simple sentence splitter
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

## Map model output labels to readable sentiment names
label_map = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
}

# Performs sentence-level sentiment analysis and computes overall document sentiment
def analyze_document(text):
    
    sentences = split_sentences(text)

    results = []
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    score_totals = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

    # Analyze each sentence individually
    for sentence in sentences:
        result = sentiment_model(
            sentence,
            truncation=True,
            max_length=512
        )[0]

        raw_label = result["label"]
        score = result["score"]

        label = label_map.get(raw_label, raw_label)

        results.append((sentence, label, score))

        counts[label] += 1
        score_totals[label] += score

    # Determine overall sentiment using weighted average
    avg_scores = {}
    for label in counts:
        if counts[label] > 0:
            avg_scores[label] = score_totals[label] / counts[label]
        else:
            avg_scores[label] = 0

    overall_sentiment = max(avg_scores, key=avg_scores.get)

    return results, counts, overall_sentiment


# Process all extracted text files and generate sentiment reports
def main():

    # Traverse extracted folder recursively (docx / ocr / pymupdf subfolders)
    for root, dirs, files in os.walk(input_folder):
        for filename in files:

            if not filename.endswith(".txt"):
                continue

            input_path = os.path.join(root, filename)

            # Determine which subfolder (docx / ocr / pymupdf)
            relative_path = os.path.relpath(root, input_folder)
            output_subfolder = os.path.join(output_folder, relative_path)

            os.makedirs(output_subfolder, exist_ok=True)

            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()

            results, counts, overall = analyze_document(text)

            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(
                output_subfolder,
                base_name + "_sentiment.txt"
            )

            with open(output_path, "w", encoding="utf-8") as out:
                out.write("Sentence-level Sentiment:\n\n")

                for sentence, label, score in results:
                    out.write(f"Sentence: {sentence}\n")
                    out.write(f"Sentiment: {label} (confidence: {score:.4f})\n")
                    out.write("-" * 50 + "\n")

                out.write("\nSummary Statistics:\n")
                out.write(f"Positive sentences: {counts['positive']}\n")
                out.write(f"Negative sentences: {counts['negative']}\n")
                out.write(f"Neutral sentences: {counts['neutral']}\n")
                out.write(f"\nOverall Document Sentiment: {overall}\n")

            print(f"Sentiment saved to: {output_path}")


if __name__ == "__main__":
    main()
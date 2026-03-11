# PDF Parser Evaluation

Overview
This project evaluates multiple PDF parsing libraries by comparing extracted text against ground truth using Word Error Rate (WER).

Project Structure
- dataset/ → Sample PDF and ground truth text
- extractors.py → PDF extraction logic
- evaluate.py → Evaluation script
- results.csv → Comparison results

Libraries Used
- pdfplumber
- pymupdf (fitz)
- pypdf2

Evaluation Metric
Word Error Rate (WER)

How to Run
pip install -r requirements.txt  
python evaluate.py

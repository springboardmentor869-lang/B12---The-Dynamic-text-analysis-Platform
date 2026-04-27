# DocuSense

DocuSense is a web-based application that leverages AI and machine learning to perform various document processing tasks. It provides APIs and a user-friendly frontend for document conversion, sentiment analysis, text summarization, and topic classification.

## Features

- **Document Conversion**: Convert PDF and DOCX files to text format
- **Sentiment Analysis**: Analyze the sentiment of text documents
- **Text Summarization**: Generate concise summaries of long documents using Hugging Face transformers
- **Topic Classification**: Classify documents into topics using BERTopic models

## Installation

1. Clone or download the repository.

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To start the server, run:
```
uvicorn api_main:app --reload
```
Note: The user must train the topic model before using the topic classifier. Ensure your training data is in the backend folder and is a .csv file named topic_dataset.csv, or update the filename on line 20 of topic_modelling.py. The file should have columns id and text.

## License

This project is licensed under the MIT License.
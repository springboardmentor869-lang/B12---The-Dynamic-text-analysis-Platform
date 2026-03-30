# B12 - The Dynamic Text Analysis Platform

## Project Overview

This project is a comprehensive text analysis platform that implements various natural language processing (NLP) tasks. It serves as a modular system for processing, analyzing, and extracting insights from textual documents. The platform is organized into 8 distinct tasks, each focusing on a specific aspect of text analysis, from document parsing to advanced topic modeling and API deployment.

The platform demonstrates a progression from basic document processing to sophisticated AI-powered analysis, utilizing modern libraries and APIs for scalable text analytics.

## Architecture and Workflow

The project follows a task-based structure where each task builds upon or complements the previous ones:

1. **Document Parsing Evaluation** → 2. **Basic Parser Implementation** → 3. **Advanced Multi-Format Parser** → 4. **Text Preprocessing** → 5. **Document Summarization** → 6. **Sentiment Analysis** → 7. **Topic Modeling** → 8. **API Deployment**

## Detailed Task Breakdown

### Task 1: PDF Parser Evaluation
- **Purpose**: Comparative analysis of PDF parsing libraries
- **Libraries Evaluated**: PyMuPDF (fitz), pdfplumber, pypdf
- **Methodology**: Word Error Rate (WER) evaluation on different document types
- **Outcome**: PyMuPDF selected as optimal parser for production use
- **Key Files**:
  - `task1/Task1_Parser_Evaluation.md`: Detailed evaluation report
  - `task1/task1_eval.py`: Evaluation script
  - `task1/truth_*.txt`: Ground truth files for comparison

### Task 2: Basic Document Parser
- **Purpose**: Implement text extraction from PDF and DOCX files
- **Libraries**: PyMuPDF for PDFs, python-docx for DOCX
- **Output**: Plain text (.txt) files
- **Key Files**:
  - `task2/pymupdf_parser.py`: Parser implementation

### Task 3: Advanced Multi-Format Parser
- **Purpose**: Parse various document formats with layout preservation
- **Libraries**: Docling
- **Supported Formats**: PDF, DOCX, PPTX, HTML, XHTML, XML, images (JPG, PNG, BMP)
- **Output**: Markdown (.md) files with preserved formatting
- **Key Files**:
  - `task3/doc_parser.py`: Parser implementation
  - `task3/processed_data/`: Output directory with parsed documents

### Task 4: Text Preprocessing Pipeline
- **Purpose**: Clean and normalize text for downstream NLP tasks
- **Techniques**: Tokenization, stopword removal, stemming, lemmatization
- **Libraries**: NLTK
- **Key Files**:
  - `task4/preprocessing.py`: Preprocessing implementation
  - `task4/stemming_results.md`: Stemming output
  - `task4/lemmatization_results.md`: Lemmatization output
  - `task4/step_by_step_demo.py`: Demonstration script

### Task 5: Document Summarization
- **Purpose**: Generate comprehensive summaries of documents
- **Approach**: LLM-powered summarization via OpenRouter API
- **Models**: Google Gemini 2.0 Flash, Meta Llama 3.3 70B
- **Key Files**:
  - `task5/summarizer_openrouter.py`: Summarization script
  - `task5/financial_summary_openrouter.md`: Sample summary output

### Task 6: Sentiment Analysis
- **Purpose**: Analyze sentiment in text documents
- **Approach**: Batch processing with LLM via OpenRouter API
- **Features**: Concurrent processing, JSON output
- **Key Files**:
  - `task6/sentiment_analyzer.py`: Sentiment analysis implementation
  - `task6/sentiment_report.md`: Analysis results
  - `task6/sentiment_about.md`: Additional sentiment data

### Task 7: Topic Modeling
- **Purpose**: Unsupervised topic discovery and classification
- **Libraries**: BERTopic, Sentence Transformers, UMAP, HDBSCAN
- **Features**: LLM-enhanced topic labeling, custom dataset training
- **Key Files**:
  - `task7/train_topic_model.py`: Model training script
  - `task7/run_inference.py`: Inference script
  - `task7/financial.csv`: Training dataset
  - `task7/models/`: Trained model files
  - `task7/results/`: Classification results and cache

### Task 8: API Deployment
- **Purpose**: Expose topic modeling capabilities via REST API
- **Framework**: FastAPI
- **Endpoints**:
  - `POST /predict`: Topic prediction for input text
  - `GET /model-info`: Model metadata
  - `DELETE /reset-session`: Session management
- **Key Files**:
  - `task8/api.py`: FastAPI application

## Project Structure

```
B12---The-Dynamic-text-analysis-Platform/
├── LICENSE
├── assets/                          # Input documents for processing
├── processed_data/                  # Root-level processed documents
│   ├── document.md
│   ├── financial_doc.md
│   ├── presentation.md
│   ├── sample1.md
│   ├── sample2.md
│   ├── sample3.md
│   └── scan.md
├── task1/                          # PDF Parser Evaluation
│   ├── task1_eval.py
│   ├── Task1_Parser_Evaluation.md
│   ├── truth_1.txt
│   ├── truth_2.txt
│   └── truth_3.txt
├── task2/                          # Basic Document Parser
│   └── pymupdf_parser.py
├── task3/                          # Advanced Multi-Format Parser
│   ├── doc_parser.py
│   └── processed_data/             # Task-specific processed documents
│       ├── document.md
│       ├── financial doc.md
│       ├── presentation.md
│       ├── sample1.md
│       ├── sample2.md
│       ├── sample3.md
│       └── scan.md
├── task4/                          # Text Preprocessing
│   ├── lemmatization_results.md
│   ├── preprocessing.py
│   ├── stemming_results.md
│   └── step_by_step_demo.py
├── task5/                          # Document Summarization
│   ├── financial_summary_openrouter.md
│   └── summarizer_openrouter.py
├── task6/                          # Sentiment Analysis
│   ├── sentiment_about.md
│   ├── sentiment_analyzer.py
│   └── sentiment_report.md
├── task7/                          # Topic Modeling
│   ├── financial.csv
│   ├── run_inference.py
│   ├── train_topic_model.py
│   ├── __pycache__/
│   ├── dataset/
│   │   └── test_document.md
│   ├── models/
│   │   ├── bertopic.md
│   │   ├── topic_centroids.json
│   │   ├── topic_mapping.json
│   └── results/
│       ├── classification_results.json
│       └── text_cache/
└── task8/                          # API Deployment
    ├── api.py
    └── __pycache__/
```

## Key Technologies and Dependencies

- **Document Processing**: PyMuPDF, python-docx, Docling
- **Text Processing**: NLTK
- **Machine Learning**: Sentence Transformers, BERTopic, UMAP, HDBSCAN
- **LLM Integration**: OpenAI API via OpenRouter
- **Web Framework**: FastAPI
- **Data Processing**: pandas, numpy
- **Environment**: Python virtual environment (.venv)

## Setup and Usage

1. **Environment Setup**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt  # Assuming requirements file exists
   ```

2. **API Deployment**:
   ```bash
   cd task8
   uvicorn api:app --reload
   ```

3. **Individual Tasks**: Each task can be run independently with appropriate input files and configurations.

## Data Flow

1. Raw documents (PDF, DOCX, etc.) → Document Parsing
2. Extracted text → Preprocessing (cleaning, normalization)
3. Processed text → Analysis (summarization, sentiment, topics)
4. Results → API endpoints for external consumption

## Future Enhancements

- Integration of all tasks into a unified pipeline
- Web-based user interface
- Support for additional document formats
- Advanced analytics and visualization
- Model fine-tuning capabilities
- Multi-language support

This platform serves as a foundation for building comprehensive text analysis solutions, demonstrating best practices in NLP pipeline development and API design.
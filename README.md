# B12 - The Dynamic Text Analysis Platform

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/backend-Python%203.9%2B-blue)
![React](https://img.shields.io/badge/frontend-React%2019-61DAFB?logo=react)

## Overview

B12 is a comprehensive, enterprise-grade text analysis platform that combines advanced Natural Language Processing (NLP) capabilities with a modern web interface. It provides end-to-end document processing, analysis, and insights through a scalable REST API powered by machine learning and LLM integration.

The platform demonstrates a complete pipeline from raw document ingestion through sophisticated AI-powered analytics, utilizing state-of-the-art libraries and APIs for production-ready text intelligence.

## Key Features

- **📄 Multi-Format Document Parsing**: Support for PDF, DOCX, PPTX, HTML, and image formats with layout preservation
- **🔍 Intelligent Text Analysis**: Document summarization, sentiment analysis, and topic modeling
- **🧠 Advanced Topic Modeling**: BERTopic-powered unsupervised topic discovery with LLM-enhanced labeling
- **📊 Interactive Visualizations**: Comprehensive charts, word clouds, and trend analysis for insights
- **🌐 RESTful API**: FastAPI backend with comprehensive endpoints for all analysis tasks
- **💻 Modern Web Interface**: React-based frontend for document processing and results visualization
- **⚡ Concurrent Processing**: Batch processing capabilities for large-scale text analysis
- **🔗 LLM Integration**: OpenRouter API integration for enhanced summarization and analysis

## Technology Stack

### Backend
- **Framework**: FastAPI with async support
- **Document Processing**: PyMuPDF, python-docx, Docling
- **Text Analysis**: NLTK, Sentence Transformers
- **Machine Learning**: BERTopic, UMAP, HDBSCAN
- **LLM Integration**: OpenRouter API
- **Deployment**: Uvicorn

### Frontend
- **Framework**: React 19
- **Language**: TypeScript
- **Build Tool**: Vite
- **Charting**: Recharts for interactive visualizations
- **PDF Export**: jsPDF, react-to-pdf
- **Markdown Rendering**: react-markdown

### Core Dependencies
- Python 3.9+
- Node.js 16+
- Virtual environment (venv)

## Project Architecture

```
┌─────────────────────────────────────┐
│   Frontend (React + TypeScript)     │
│   - Document Upload & Processing   │
│   - Results Visualization           │
│   - PDF Export Functionality        │
└────────┬────────────────────────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────────┐
│   Backend (FastAPI)                 │
├─────────────────────────────────────┤
│   ┌─────────────────────────────┐   │
│   │ Analysis Routers            │   │
│   │ - Topic Modeling            │   │
│   │ - Sentiment Analysis        │   │
│   │ - Document Summarization    │   │
│   └─────────────────────────────┘   │
│   ┌─────────────────────────────┐   │
│   │ NLP Services & Pipelines    │   │
│   │ - Async Task Processing     │   │
│   │ - Model Inference           │   │
│   │ - Data Extraction           │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   ML/Data Layer                     │
│ - BERTopic Models                   │
│ - Pretrained Transformers           │
│ - External LLM APIs                 │
└─────────────────────────────────────┘
```

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- pip and npm package managers

### Installation

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd B12---The-Dynamic-text-analysis-Platform
```

#### 2. Setup Backend
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file in backend directory with necessary API keys
```

#### 3. Setup Frontend
```bash
cd frontend

# Install dependencies
npm install

# Build TypeScript
npm run build
```

## Running the Application

### Start Backend API
```bash
cd backend
uvicorn main:app --reload
# API will be available at http://localhost:8000
# Interactive API docs at http://localhost:8000/docs
```

### Start Frontend Development Server
```bash
cd frontend
npm run dev
# Application will be available at http://localhost:5173
```

### Build for Production
```bash
# Frontend
cd frontend
npm run build

# Backend is ready for deployment with any ASGI server
```

## API Documentation

### Base URL
```
http://localhost:8000
```

### Health Check
```http
GET /health
```

### Topic Modeling Endpoints
```http
POST /predict          # Predict topics for input text
GET /model-info        # Get model metadata
DELETE /reset-session  # Reset analysis session
```

### Sentiment Analysis Endpoints
```http
POST /sentiment        # Analyze sentiment in documents
```

### Summarization Endpoints
```http
POST /summarize        # Generate document summaries
```

**Full API documentation available at `/docs` when backend is running.**

## Project Structure

```
B12---The-Dynamic-text-analysis-Platform/
├── backend/                         # FastAPI application
│   ├── main.py                      # Application entry point
│   ├── core/
│   │   └── config.py               # Configuration management
│   ├── models/
│   │   └── schemas.py              # Data models & validation
│   ├── routers/
│   │   ├── topic.py                # Topic modeling endpoints
│   │   ├── sentiment.py            # Sentiment analysis endpoints
│   │   └── summarize.py            # Summarization endpoints
│   └── services/
│       ├── async_tasks.py          # Async task processing
│       ├── extractor.py            # Text extraction utilities
│       └── pipelines.py            # ML inference pipelines
├── frontend/                        # React application
│   ├── src/
│   │   ├── App.tsx                 # Main component
│   │   ├── main.tsx                # Entry point
│   │   ├── types.ts                # TypeScript types
│   │   └── assets/                 # Static assets
│   ├── index.html                  # HTML template
│   ├── package.json                # Frontend dependencies
│   ├── vite.config.ts              # Vite configuration
│   └── tsconfig.json               # TypeScript configuration
├── task1/                          # Parser Evaluation & Research
│   ├── task1_eval.py               # Library comparison script
│   └── Task1_Parser_Evaluation.md  # Evaluation report
├── task2/                          # Basic Parser Implementation
│   └── pymupdf_parser.py           # PDF/DOCX extraction
├── task3/                          # Advanced Parser
│   └── doc_parser.py               # Multi-format parsing with Docling
├── task4/                          # Text Preprocessing
│   ├── preprocessing.py            # Tokenization, stemming, lemmatization
│   └── step_by_step_demo.py        # Pipeline demonstration
├── task5/                          # Document Summarization
│   └── summarizer_openrouter.py   # LLM-based summarization
├── task6/                          # Sentiment Analysis
│   └── sentiment_analyzer.py       # Multi-batch sentiment processing
├── task7/                          # Topic Modeling
│   ├── train_topic_model.py        # BERTopic model training
│   ├── run_inference.py            # Topic inference
│   ├── models/                     # Trained model artifacts
│   └── results/                    # Classification results
├── task8/                          # Legacy API Implementation
│   └── api.py                      # Original FastAPI setup
├── processed_data/                 # Sample outputs
├── assets/                         # Input documents
├── LICENSE
└── README.md                       # This file
```

## Workflow & Data Pipeline

```
Raw Documents (PDF, DOCX, PPTX, etc.)
           ↓
   Document Parsing (Task 3)
 [Docling + PyMuPDF Fallback]
           │
           ├──────────────────────────────────────────┐
           │                                          │
           ↓                                          ↓
  Raw, Formatted Text                     [Archived / Standalone Utility]
(Maintains natural grammar)                 Text Preprocessing (Task 4)
           │                               (Not used in current pipeline)
           │
   ┌───────┼──────────────┐                              
   ↓       ↓              ↓                              
 Task 5   Task 6        Task 7
(Summ.)  (Sent.)       (Topic)
 [LLM]  [FinBERT]    [BERTopic]
   │       │              │                              
   └───────┼──────────────┘
           ↓
   REST API (FastAPI Backend)
           ↓
   Web Interface (React Frontend)
           ↓
   Results, Dashboards & Insights
```

## Core Features in Detail

### 📄 Document Processing
- **Multi-format support**: PDF, DOCX, PPTX, HTML, XML, images
- **Layout preservation**: Maintains document structure in Markdown output
- **Batch processing**: Handle multiple documents concurrently
- **Format evaluation**: Comparative analysis of parsing libraries with WER metrics

### 📊 Interactive Visualizations
- **Word Clouds**: Visual representation of key themes and keywords
- **Topic Distribution Charts**: Bar charts showing all discovered topics with confidence scores
- **Sentiment Distribution**: Pie charts for positive/negative/neutral sentiment breakdowns
- **Sentiment Trend Analysis**: Scatter plots showing sentiment evolution through the document
- **Custom Tooltips**: Interactive hover information for detailed insights
- **PDF Export**: All visualizations included in exported reports


### 🧠 Intelligent Analysis
- **Sentiment Analysis**: LLM-powered sentiment detection with concurrent processing
- **Document Summarization**: Extract key information using advanced LLMs (Gemini, Llama)
- **Topic Modeling**: Unsupervised topic discovery with semantic understanding
- **Text Preprocessing**: Advanced NLP preprocessing pipeline

### 🔗 Extensible Architecture
- **Modular design**: Each analysis component is independently deployable
- **Async-first**: Built for high-throughput concurrent processing
- **LLM integration**: Seamless integration with external AI APIs
- **RESTful endpoints**: Standard HTTP API for all functionality

## Development

### Running Tests & Validation

```bash
# Example: Run document parser
python task3/doc_parser.py

# Example: Run preprocessing demo
python task4/step_by_step_demo.py

# Example: Run sentiment analysis
python task6/sentiment_analyzer.py

# Example: Train topic model
python task7/train_topic_model.py
```

### Code Quality

```bash
cd frontend
npm run lint          # Run ESLint
npm run build         # Verify TypeScript compilation
```

### Environment Variables

Backend requires the following environment variables (`.env` file):
```
OPENROUTER_API_KEY=your_api_key_here
DATABASE_URL=optional_database_url
LOG_LEVEL=INFO
```

## Deployment

### Production Deployment

#### Backend (Using Gunicorn + Uvicorn)
```bash
# Install production server
pip install gunicorn

# Run with multiple workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend (Static Files)
```bash
# Build for production
npm run build

# Serve with your preferred web server (nginx, Apache, etc.)
# Outputs to: frontend/dist/
```

#### Docker Deployment (Optional)
Create `Dockerfile` for backend:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Performance Optimization

- **Backend**: Consider using Redis for caching model predictions
- **Frontend**: Implement lazy loading for large document uploads
- **Database**: Monitor query performance with appropriate indexing
- **API**: Implement rate limiting for production use

## Troubleshooting

### Common Issues

**Issue**: Backend fails to start with model loading errors
```bash
# Solution: Ensure all model dependencies are installed
pip install -r requirements.txt
python -c "import torch; import transformers; print('Dependencies OK')"
```

**Issue**: Frontend cannot connect to backend API
```bash
# Solution: Check backend is running and CORS is properly configured
# Verify Backend is running on http://localhost:8000
# Check frontend environment configuration
```

**Issue**: Out of memory errors during topic modeling
```bash
# Solution: Reduce batch size in task7/train_topic_model.py
# or use GPU acceleration if available
```

**Issue**: API returns 500 errors during document processing
```bash
# Solution: Check backend logs and ensure OpenRouter API key is valid
# Verify input documents are in supported formats
```

## Performance Benchmarks

- **Document Parsing**: ~50-100 KB/s depending on format complexity
- **Text Preprocessing**: ~10,000 tokens/second
- **Topic Modeling Inference**: <1s per document
- **API Response Time**: <500ms for single document analysis

## API Response Examples

### Topic Prediction
```json
{
  "topics": [
    {
      "id": 0,
      "label": "Finance",
      "probability": 0.95
    },
    {
      "id": 1,
      "label": "Technology",
      "probability": 0.03
    }
  ],
  "processing_time_ms": 245
}
```

### Sentiment Analysis
```json
{
  "sentiment": "positive",
  "confidence": 0.92,
  "entities": ["company", "growth", "innovation"],
  "summary": "Document discusses positive business developments"
}
```

### Document Summary
```json
{
  "original_length": 2500,
  "summary_length": 450,
  "summary": "Key points about the document...",
  "key_phrases": ["metric1", "metric2", "metric3"]
}
```

## Research & Evaluation

The project includes comprehensive research documentation:
- **Parser Evaluation** (Task 1): Comparative analysis of PDF parsing libraries
- **Preprocessing Techniques** (Task 4): Detailed results and comparisons
- **Model Performance** (Task 7): Topic modeling accuracy and metrics

See individual task directories for detailed reports and evaluation results.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards
- Python: Follow PEP 8 guidelines
- TypeScript: Use provided ESLint configuration
- Documentation: Update README and add docstrings for new functions
- Testing: Include test cases for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **BERTopic**: Advanced topic modeling framework
- **Sentence Transformers**: Semantic embeddings
- **OpenRouter**: LLM API aggregation
- **FastAPI**: Modern web framework
- **React**: UI framework

## Project Timeline

- **Phase 1**: Document parsing and evaluation
- **Phase 2**: Text preprocessing pipeline
- **Phase 3**: Advanced analysis modules (summarization, sentiment)
- **Phase 4**: Topic modeling integration
- **Phase 5**: API deployment and backend integration
- **Phase 6**: Frontend development and visualization

## Roadmap

### v1.1 (Planned)
- [ ] Multi-language support
- [ ] Advanced visualization dashboard
- [ ] Real-time collaborative analysis
- [ ] Model fine-tuning interface

### v1.2 (Planned)
- [ ] GraphDB integration for entity relationships
- [ ] Knowledge graph extraction
- [ ] Advanced search capabilities
- [ ] Batch processing optimization

### v2.0 (Long-term)
- [ ] Distributed processing support
- [ ] Custom model training UI
- [ ] Advanced reporting and analytics
- [ ] Enterprise integrations

## Support & Contact

For issues, feature requests, or questions:
- **Issues**: Use GitHub Issues tracker
- **Documentation**: See task-specific markdown files
- **API Docs**: Visit `http://localhost:8000/docs` when running backend

## Quick Links

- [Backend API Docs](http://localhost:8000/docs)
- [Frontend Dev Server](http://localhost:5173)
- [Project License](LICENSE)
- [Detailed API Specification](backend/README.md)

---

**Last Updated**: March 2026
**Maintainer**: B12 Development Team
**Status**: Active Development
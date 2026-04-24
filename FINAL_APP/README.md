# Document Intelligence Dashboard

A high-performance document analysis system that leverages Large Language Models (LLMs) and advanced Topic Modeling to extract meaningful insights from unstructured text. This project provides automated summarization, sentiment analysis, and theme discovery through a modern, responsive dashboard.

## 🚀 Key Features

-   **Intelligent Summarization**: Context-aware document summaries using the Qwen2.5 model.
-   **Sentiment Analysis**: Granular sentiment tracking across document segments.
-   **Topic Modeling**: Advanced theme discovery using BERTopic (UMAP + KMeans).
-   **LLM-Powered Labeling**: Automatically generates human-readable labels for discovered topics via Ollama.
-   **Real-time Dashboard**: A sleek, dark-themed UI built with Streamlit for intuitive data exploration.

## 🛠️ Technology Stack

-   **Backend**: Python, FastAPI, Uvicorn
-   **Frontend**: Streamlit
-   **NLP / AI**: BERTopic, Sentence-Transformers, Scikit-Learn
-   **LLM Integration**: Ollama (Qwen2.5:3b)

---

## 📋 Prerequisites

Before running the project, ensure you have the following installed:

1.  **Python 3.10+**
2.  **Ollama**: [Download here](https://ollama.com/)
    -   After installation, pull the required model:
        ```bash
        ollama pull qwen2.5:3b
        ```

---

## 📥 Getting Started

### 1. Environment Setup
Clone the repository and create a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Model Training (Initial Setup)
The system needs to be trained on your base dataset to understand the topics.
```bash
cd backend
python train_model.py
```
*Note: Ensure Ollama is running in the background before starting this step.*

---

## 🏃 Running the Application

To run the full application, you need to start both the Backend API and the Frontend Dashboard in separate terminals.

### Step 1: Start the Backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Step 2: Start the Frontend
```bash
cd frontend
python -m streamlit run app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```text
├── backend/
│   ├── data/               # Training datasets (CSV)
│   ├── services/           # Core logic (AI, Topic Modeling)
│   ├── storage/            # Saved models and artifacts
│   ├── main.py             # FastAPI entry point
│   └── train_model.py      # Initial model training script
├── frontend/
│   ├── components/         # UI View components
│   ├── pages/              # Streamlit page definitions
│   └── app.py              # Dashboard entry point
└── requirements.txt        # Project dependencies
```

---

## 🛡️ License
This project is developed as part of an internship project for Document Intelligence and Analysis.

# Dynamic Text Analysis Platform

A full-stack application that provides powerful text analysis features, including document conversion, text summarization, sentiment analysis, and topic modeling.

## Project Structure

- **`backend/`**: A Python backend built with FastAPI to handle the AI/ML tasks (summarization, sentiment analysis, topic modeling) and document parsing.
- **`frontend/`**: A web frontend built with Vite and Node.js.

---

## 🚀 Running the Application

### 1. Backend (FastAPI)

Open a terminal and follow these steps:

```bash
# Navigate to the backend directory
cd backend

# Install the Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app:app --reload
```
*The backend server will run at `http://localhost:8000`*

### 2. Frontend (Vite)

Open a **new** terminal and follow these steps:

```bash
# Navigate to the frontend directory
cd frontend

# Install Node modules (if not already installed)
npm install

# Start the frontend development server
npm run dev
```
*The frontend will typically run at `http://localhost:5173` (check the terminal output for the exact URL).*

---

## 🛠️ Features

- **Document Conversion**: Extract and parse text from uploaded files (e.g., PDFs).
- **Text Summarization**: Automatically generate concise summaries of long documents.
- **Sentiment Analysis**: Analyze the general tone and sentiment of the provided text.
- **Topic Modeling**: Automatically classify and infer the main topics discussed in the text.

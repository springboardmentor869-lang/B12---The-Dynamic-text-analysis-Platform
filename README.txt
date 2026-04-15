# Dynamic Text Analysis Platform

## Overview
The Dynamic Text Analysis Platform is a full-stack web application that allows users to upload documents and perform various Natural Language Processing (NLP) tasks such as text conversion, summarization, sentiment analysis, and topic classification.

---

## Features
- Document upload (PDF/Text)
- Text extraction (conversion)
- Text summarization
- Sentiment analysis
- Topic classification

---

## Tech Stack

### Frontend
- React.js
- CSS

### Backend
- FastAPI (Python)
- NLP libraries (Transformers, NLTK, Scikit-learn)

---

## Project Structure
The-Dynamic-text-analysis-Platform/
│── backend/
│── frontend/
│── requirements.txt
│── README.md

---

## Setup Instructions

### Step 1: Clone the repository

---

### Step 2: Run Backend

Backend will run at: http://127.0.0.1:8000

---

### Step 3: Run Frontend

Open a new terminal:
cd frontend
npm install
npm start

Frontend will run at: http://localhost:3000

---

## API Endpoints

- POST /convert → Extract text from document  
- POST /summarize → Generate summary  
- POST /sentiment → Perform sentiment analysis  
- POST /topic → Predict topic  

---

Common Commands

uv run uvicorn main:app --reload
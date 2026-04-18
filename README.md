# B12 - The Dynamic Text Analysis Platform

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Tech](https://img.shields.io/badge/Tech-React%20%7C%20FastAPI%20%7C%20AI-blue)

An intelligent, state-of-the-art document analysis platform that leverages advanced NLP models to extract insights, summarize text, analyze sentiment, and classify topics in real-time.

---

## 🚀 Key Features

- **📄 Universal Document Parsing**: Seamlessly extract text from various file formats (PDFs, text, etc.) using high-fidelity parsing engines.
- **✨ AI-Powered Summarization**: Generate concise, context-aware summaries of long documents using state-of-the-art transformer models.
- **📊 Sentiment Intelligence**: Real-time sentiment analysis with scoring across multiple dimensions to gauge the emotional tone of text.
- **🏷️ Zero-Shot Topic Classification**: Automatically categorize documents into semantic topics without requiring pre-labeled training data.
- **🎨 Interactive Dashboard**: Dynamic visualizations including sentiment charts, topic distributions, and interactive word clouds.
- **⚡ Parallel Processing**: High-performance backend utilizing asynchronous task execution for lightning-fast analysis.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: [React 19](https://react.dev/) + [Vite](https://vitejs.dev/)
- **Styling**: Vanilla CSS with modern Glassmorphism aesthetics
- **Animations**: [Framer Motion](https://www.framer.com/motion/)
- **Charts**: [Recharts](https://recharts.org/)
- **Icons**: [Lucide React](https://lucide.dev/)

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **AI Models**: [Hugging Face Transformers](https://huggingface.co/docs/transformers/index) (PyTorch)
- **NLP Utilities**: Sentence-Transformers, PyPDF2
- **Server**: Uvicorn

---

## 📂 Project Structure

```bash
dynamic_text_analysis/
├── frontend/             # React source code & Vite configuration
│   ├── src/              # App components, styles, and logic
│   └── public/           # Static assets
├── backend/              # FastAPI server & AI logic
│   ├── summarization/    # Summarization pipeline
│   ├── topic_training/   # Topic classification logic
│   └── preprocessing/    # Text cleaning and parsing
└── README.md             # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python app.py
   # Or using uvicorn directly:
   # uvicorn app:app --reload
   ```

### 2. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

---

## 🤝 Contribution

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License
This project is licensed under the MIT License.

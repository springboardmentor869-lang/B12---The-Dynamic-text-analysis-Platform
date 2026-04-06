# Dynamic Text Analyzer

Fullstack PDF analysis app with:
- FastAPI backend for topic modeling, sentiment analysis, and summarization
- React + Vite frontend for upload and results visualization

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) installed
- Node.js 18+ and npm

## Project Structure

- `backend/` FastAPI service
- `frontend/` React app
- `.env` backend configuration
- `pyproject.toml` Python dependencies (managed by uv)

## 1. Configure Environment

Create or update `.env` in project root:

```env
GOOGLE_AI_API_KEY="your_google_ai_key"
# Optional (if you want LM Studio instead of Gemini)
# use_lm_studio=true
# LM_STUDIO_URL=http://localhost:1234/v1
```

## 2. Install Dependencies

From project root:

```bash
uv sync
```

Frontend dependencies:

```bash
cd frontend
npm install
```

## 3. Run Backend (uv)

Open terminal 1 at project root:

```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## 4. Run Frontend

Open terminal 2:

```bash
cd frontend
npm run dev
```

Open the URL shown by Vite (default: `http://localhost:3000`).

## 5. How Frontend Connects to Backend

The frontend dev server proxies API routes to backend `localhost:8000` via `frontend/vite.config.js`:

- `/analyze`
- `/topic-model`
- `/sentiment`
- `/summarize`
- `/health`

So in development, frontend requests to these paths automatically hit the backend.

## Common Commands

Backend lint-free run:

```bash
uv run uvicorn backend.main:app --reload
```

Frontend production build:

```bash
cd frontend
npm run build
npm run preview
```

## Troubleshooting

- If summarizer says API key is missing, verify `.env` is in project root and contains `GOOGLE_AI_API_KEY`.
- If frontend cannot reach backend, ensure backend is running on port `8000`.
- If CORS/proxy issues appear, confirm `frontend/vite.config.js` proxy targets `http://localhost:8000`.

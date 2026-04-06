from typing import Optional

from openai import OpenAI
from core.config import settings

try:
    from google import genai as google_genai
except ImportError:  # pragma: no cover - compatibility fallback
    google_genai = None
    import google.generativeai as legacy_genai
else:
    legacy_genai = None


class Summarizer:
    """Text summarization service using Gemini or LM Studio."""

    _instance: Optional["Summarizer"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.use_lm_studio = settings.use_lm_studio
        self.lm_studio_url = settings.lm_studio_url
        self.use_local_fallback = False

        if not self.use_lm_studio:
            if not settings.google_ai_api_key:
                self.use_local_fallback = True
                self.gemini_client = None
            elif google_genai is not None:
                self.gemini_client = google_genai.Client(api_key=settings.google_ai_api_key)
            else:
                legacy_genai.configure(api_key=settings.google_ai_api_key)
                self.gemini_client = legacy_genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.gemini_client = None

        self._initialized = True

    def summarize(self, text: str, max_length: int = 1000) -> dict:
        """
        Summarize text.

        Returns dict with summary and word_count.
        """
        if not text.strip():
            return {"summary": "No text to summarize.", "word_count": 0}

        try:
            if self.use_local_fallback:
                summary_text = self._summarize_locally(text, max_length)
            elif self.use_lm_studio:
                summary_text = self._summarize_with_lm_studio(text, max_length)
            else:
                summary_text = self._summarize_with_gemini(text, max_length)

            return {
                "summary": summary_text,
                "word_count": len(summary_text.split()),
            }
        except Exception as e:
            return {"summary": f"Error generating summary: {str(e)}", "word_count": 0}

    def _summarize_locally(self, text: str, max_length: int) -> str:
        """Fallback extractive summary when no external LLM is configured."""
        cleaned = " ".join(text.split())
        if not cleaned:
            return "No text to summarize."

        sentences = [
            sentence.strip()
            for sentence in cleaned.replace("!", ".").replace("?", ".").split(".")
            if sentence.strip()
        ]

        if not sentences:
            words = cleaned.split()
            return " ".join(words[:max_length]).strip()

        selected_sentences = []
        current_words = 0
        target_words = min(max_length, 180)

        for sentence in sentences:
            sentence_words = sentence.split()
            if not sentence_words:
                continue
            if selected_sentences and current_words + len(sentence_words) > target_words:
                break
            selected_sentences.append(sentence)
            current_words += len(sentence_words)

        if not selected_sentences:
            return " ".join(cleaned.split()[:target_words]).strip()

        summary = ". ".join(selected_sentences).strip()
        if not summary.endswith("."):
            summary += "."

        return f"{summary}\n\nNote: Generated with local fallback because no Gemini API key is configured."

    def _summarize_with_gemini(self, text: str, max_length: int) -> str:
        """Summarize using Google Gemini."""
        prompt = (
            f"Summarize the following text in {max_length} words or less, "
            f"focusing on key points:\n\n{text}"
        )

        if google_genai is not None:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            summary = response.text.strip()
        else:
            response = self.gemini_client.generate_content(prompt)
            summary = (response.text or "").strip()

        return summary if summary else "Summary generation failed."

    def _summarize_with_lm_studio(self, text: str, max_length: int) -> str:
        """Summarize using LM Studio (local model)."""
        client = OpenAI(
            base_url=self.lm_studio_url,
            api_key="lm-studio",
        )

        prompt = (
            f"Summarize the following text in {max_length} words or less, "
            f"focusing on key points:\n\n{text}"
        )

        response = client.chat.completions.create(
            model="qwen/qwen3-4b-2507",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_length,
            temperature=0.7,
        )

        summary = response.choices[0].message.content.strip()
        return summary if summary else "Summary generation failed."


# Singleton instance - initialized lazily
_summarizer: Optional[Summarizer] = None


def get_summarizer() -> Summarizer:
    """Get or create summarizer instance."""
    global _summarizer
    if _summarizer is None:
        _summarizer = Summarizer()
    return _summarizer

import os
from typing import Optional

from google import genai
from openai import OpenAI
from core.config import settings


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

        if not self.use_lm_studio:
            if not settings.google_ai_api_key:
                raise ValueError(
                    "GOOGLE_AI_API_KEY not set. "
                    "Set it in .env or set use_lm_studio=true for LM Studio."
                )
            self.gemini_client = genai.Client(api_key=settings.google_ai_api_key)

        self._initialized = True

    def summarize(self, text: str, max_length: int = 1000) -> dict:
        """
        Summarize text.

        Returns dict with summary and word_count.
        """
        if not text.strip():
            return {"summary": "No text to summarize.", "word_count": 0}

        try:
            if self.use_lm_studio:
                summary_text = self._summarize_with_lm_studio(text, max_length)
            else:
                summary_text = self._summarize_with_gemini(text, max_length)

            return {
                "summary": summary_text,
                "word_count": len(summary_text.split()),
            }
        except Exception as e:
            return {"summary": f"Error generating summary: {str(e)}", "word_count": 0}

    def _summarize_with_gemini(self, text: str, max_length: int) -> str:
        """Summarize using Google Gemini."""
        prompt = (
            f"Summarize the following text in {max_length} words or less, "
            f"focusing on key points:\n\n{text}"
        )

        response = self.gemini_client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        summary = response.text.strip()
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

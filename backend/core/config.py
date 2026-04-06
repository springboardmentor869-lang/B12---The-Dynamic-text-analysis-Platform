from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # API Settings
    app_name: str = "Dynamic Text Analyzer"
    debug: bool = False

    # File Upload Settings
    max_upload_size_mb: int = 50
    upload_dir: Path = PROJECT_ROOT / "backend" / "uploads"
    temp_markdown_dir: Path = PROJECT_ROOT / "backend" / "temp_markdown"

    # Gemini API
    google_ai_api_key: str = ""

    # LM Studio (optional alternative to Gemini)
    lm_studio_url: str = "http://localhost:1234/v1"
    use_lm_studio: bool = False

    # Model paths
    bertopic_model_dir: Path = PROJECT_ROOT / "models" / "bertopic_20newsgroups"
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # Topic modeling threshold
    similarity_threshold: float = 0.20

    class Config:
        env_file = PROJECT_ROOT / ".env"
        env_file_encoding = "utf-8"

    @field_validator("debug", mode="before")
    @classmethod
    def coerce_debug_value(cls, value: Any) -> bool:
        """Accept common environment-style debug values without crashing."""
        if isinstance(value, bool):
            return value
        if value is None:
            return False

        normalized = str(value).strip().lower()
        truthy = {"1", "true", "yes", "on", "debug", "development", "dev"}
        falsy = {"0", "false", "no", "off", "release", "production", "prod"}

        if normalized in truthy:
            return True
        if normalized in falsy:
            return False

        raise ValueError("debug must be a boolean-like value")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.temp_markdown_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()

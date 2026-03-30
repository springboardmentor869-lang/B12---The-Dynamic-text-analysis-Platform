from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Dynamic Text Analyzer API"
    version: str = "1.0.0"

settings = Settings()
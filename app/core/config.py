import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    LLM_FALLBACK_ENABLED: bool = os.getenv("LLM_FALLBACK_ENABLED", "true").lower() in {"1", "true", "yes"}

    # Anthropic
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

    # Document types
    ALLOWED_DOCUMENT_TYPES: list[str] = [".pdf", ".xlsx"]

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # OCR settings
    OCR_ENABLED: bool = os.getenv("OCR_ENABLED", "true").lower() in {"1", "true", "yes"}
    OCR_DPI: int = int(os.getenv("OCR_DPI", "600"))
    OCR_KEEP_IMAGES: bool = os.getenv("OCR_KEEP_IMAGES", "false").lower() in {"1", "true", "yes"}
    OCR_MIN_TEXT_CHARS: int = int(os.getenv("OCR_MIN_TEXT_CHARS", "100"))

settings = Settings()

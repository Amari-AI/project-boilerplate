import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic API Key - should be set via environment variable
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Document types
    ALLOWED_DOCUMENT_TYPES: list[str] = [".pdf", ".xlsx"]

settings = Settings()

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    # TODO: Add configuration options

    # Anthropic Claude API Key
    API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Document types
    ALLOWED_DOCUMENT_TYPES: list[str] = [".pdf", ".xlsx", ".xls"]


settings = Settings()

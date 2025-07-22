import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # TODO: Add configuration options
    model_config = SettingsConfigDict(env_file=".env")

    # Anthropic API Key
    anthropic_api_key: str = ""
    
    # Document types
    ALLOWED_DOCUMENT_TYPES: list[str] = [".pdf", ".xlsx", ".xls"]

settings = Settings()

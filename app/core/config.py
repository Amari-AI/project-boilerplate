import os
from pydantic_settings import BaseSettings
import dotenv

dotenv.load_dotenv()


class Settings(BaseSettings):
    # TODO: Add configuration options

    # OpenAI API Key
    API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Document types
    ALLOWED_DOCUMENT_TYPES: list[str] = [".pdf", ".xlsx"]

settings = Settings()

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # TODO: Add configuration options

    # OpenAI API Key
    API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # ANTHROPIC_API_KEY: 
    
    # Form URL
    # FORM_URL: str = "https://forms.gle/11kUya5nTebvFBgn7"
    FORM_URL: str = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSemlBSMvQsQZnAudDXMWXGldJGdZW6VkoDAwbQKsuTGlgZfNg/formResponse"
    
    # Document types
    ALLOWED_DOCUMENT_TYPES: list[str] = [".pdf", ".xlsx"]

settings = Settings()

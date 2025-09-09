from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Atabot-Lite"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # LLM Configuration
    POE_API_KEY: str
    POE_MODEL: str = "ChatGPT-3.5-Turbo"
    
    # Embedding Configuration (optional)
    VOYAGE_API_KEY: Optional[str] = None
    VOYAGE_MODEL: str = "voyage-3.5-lite"
    
    # Chatbot Configuration
    MAX_CONTEXT_LENGTH: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
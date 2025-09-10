from pydantic_settings import BaseSettings

class PerformanceSettings(BaseSettings):
    # Cache settings
    CACHE_DEFAULT_TTL: int = 3600
    EMBEDDING_CACHE_TTL: int = 86400
    RESPONSE_CACHE_TTL: int = 1800
    
    # Performance settings
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30
    
    # Memory management
    MAX_CACHE_SIZE_MB: int = 100
    MAX_SESSION_HISTORY: int = 50
    
    class Config:
        env_file = ".env"

performance_settings = PerformanceSettings()

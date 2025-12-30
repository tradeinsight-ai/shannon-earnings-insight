from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    alpha_vantage_api_key: str
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS
    frontend_url: str = "http://localhost:5173"
    
    # Rate Limiting
    alpha_vantage_rate_limit: int = 999  # requests per minute
    
    # Search Filtering
    filter_us_equities_only: bool = True  # Only return US-listed company stocks
    
    # Whisper Transcription
    whisper_model_size: str = "base"  # tiny, base, small, medium, large-v2, large-v3
    whisper_chunk_duration_ms: int = 3000  # Recording chunk duration in milliseconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

"""
Application Configuration
Uses pydantic-settings for environment variable management.
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Resume-Job Matching System"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/resume_matcher"
    
    # For SQLite fallback (development)
    USE_SQLITE: bool = False
    SQLITE_URL: str = "sqlite+aiosqlite:///./resume_matcher.db"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # LLM Settings (Groq Cloud API)
    LLM_API_URL: str = "https://api.groq.com/openai/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_ENABLED: bool = True
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 16 * 1024 * 1024  # 16MB
    UPLOAD_DIR: str = "data/uploads"
    
    # CORS - comma-separated string from env, or default list for local dev
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string or allow all with *."""
        origins = self.CORS_ORIGINS.strip()
        if origins == "*":
            return ["*"]
        return [o.strip() for o in origins.split(",") if o.strip()]
    
    @property
    def database_url(self) -> str:
        """Get the appropriate database URL."""
        if self.USE_SQLITE:
            return self.SQLITE_URL
        return self.DATABASE_URL
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()

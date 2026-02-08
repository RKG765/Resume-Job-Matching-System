"""
Application Configuration
Uses pydantic-settings for environment variable management.
"""

from pydantic_settings import BaseSettings
from typing import Optional
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
    
    # LLM Settings
    LLM_API_URL: str = "http://127.0.0.1:1234/v1"
    LLM_MODEL: str = "deepseek-r1-distill-llama-8b"
    LLM_ENABLED: bool = True
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 16 * 1024 * 1024  # 16MB
    UPLOAD_DIR: str = "data/uploads"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
    
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

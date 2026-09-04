"""
Voice Shield Backend Configuration
==================================
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    APP_NAME: str = "Voice Shield"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Voice Clone Detection System"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "voice-shield-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # ML Service
    ML_API_URL: str = "https://deepvoiceguard-api.onrender.com/predict"
    ML_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./voiceshield.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

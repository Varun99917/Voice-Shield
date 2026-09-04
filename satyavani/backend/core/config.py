"""
SatyVaani Backend Configuration
===============================
All settings in one place
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application Settings
    """
    
    # App Info
    APP_NAME: str = "SatyVaani"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Voice Clone Detection System"
    
    # Environment
    ENVIRONMENT: str = "development"  # development / production
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/satyavani"
    
    # For SQLite (simpler for hackathon)
    SQLITE_URL: str = "sqlite+aiosqlite:///./satyavani.db"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # ML Model Settings
    MODEL_PATH: str = "./models/trained"
    RISK_THRESHOLDS: dict = {
        "low": 60,      # 0-60% = Low risk (safe)
        "medium": 40,   # 40-60% = Medium risk
        "high": 20,     # 20-40% = High risk
        "critical": 0   # 0-20% = Critical (definite threat)
    }
    
    # Audio Settings
    AUDIO_CHUNK_SIZE: int = 2  # seconds
    SAMPLE_RATE: int = 16000
    
    # CORS (allow frontend to connect)
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # React admin dashboard
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Alternative
    ]
    
    # Notification Settings
    ENABLE_EMAIL: bool = True
    ENABLE_SMS: bool = True
    ENABLE_PUSH: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Helper function
def get_settings() -> Settings:
    """Get application settings"""
    return settings

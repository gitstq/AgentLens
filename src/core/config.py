"""
Application configuration settings.
"""

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    APP_NAME: str = "AgentLens"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{Path(__file__).parent.parent.parent}/data/agentlens.db"
    )
    
    # Storage
    DATA_DIR: Path = Path(__file__).parent.parent.parent / "data"
    SESSIONS_DIR: Path = DATA_DIR / "sessions"
    
    # Analysis
    MAX_SESSION_SIZE_MB: int = 100
    DEFAULT_TOKEN_PRICE_PER_1K: float = 0.01
    
    class Config:
        env_file = ".env"


settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

"""
GAIM Lab v3.0 - Backend Configuration
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment
load_dotenv()


class Settings(BaseSettings):
    """Application Settings"""
    
    # Server
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent
    UPLOADS_DIR: Path = PROJECT_ROOT / "uploads"
    OUTPUT_DIR: Path = PROJECT_ROOT / "output"
    CACHE_DIR: Path = PROJECT_ROOT / "cache"
    
    # Analysis
    MAX_VIDEO_SIZE_MB: int = int(os.getenv("MAX_VIDEO_SIZE_MB", "2048"))
    ANALYSIS_TIMEOUT_SECONDS: int = int(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "1800"))
    
    # Whisper
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "small")
    WHISPER_LANGUAGE: str = os.getenv("WHISPER_LANGUAGE", "ko")
    
    # Evaluation dimensions
    DIMENSION_CONFIG: dict = {
        "teaching_expertise": {"name": "수업 전문성", "max_score": 20},
        "teaching_method": {"name": "교수학습 방법", "max_score": 20},
        "communication": {"name": "판서 및 언어", "max_score": 15},
        "teaching_attitude": {"name": "수업 태도", "max_score": 15},
        "student_engagement": {"name": "학생 참여", "max_score": 15},
        "time_management": {"name": "시간 배분", "max_score": 10},
        "creativity": {"name": "창의성", "max_score": 5}
    }
    
    class Config:
        env_file = ".env"


settings = Settings()

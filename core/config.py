"""
GAIM Lab v3.0 - Core Configuration
"""

from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CORE_ROOT = Path(__file__).parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
FRONTEND_ROOT = PROJECT_ROOT / "frontend"

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "output"
UPLOADS_DIR = PROJECT_ROOT / "uploads"
CACHE_DIR = PROJECT_ROOT / "cache"

# Create directories if not exist
for dir_path in [OUTPUT_DIR, UPLOADS_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


class Settings:
    """Application settings"""
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Server settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Analysis settings
    MAX_VIDEO_SIZE_MB: int = int(os.getenv("MAX_VIDEO_SIZE_MB", "2048"))
    ANALYSIS_TIMEOUT_SECONDS: int = int(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "1800"))
    
    # Whisper settings
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "small")
    WHISPER_LANGUAGE: str = os.getenv("WHISPER_LANGUAGE", "ko")
    
    # Video processing
    FRAME_SAMPLE_FPS: int = 1  # Extract 1 frame per second
    AUDIO_SAMPLE_RATE: int = 16000
    
    # Evaluation dimensions (Korean elementary teacher exam criteria)
    DIMENSION_CONFIG = {
        "teaching_expertise": {"name": "수업 전문성", "max_score": 20},
        "teaching_method": {"name": "교수학습 방법", "max_score": 20},
        "communication": {"name": "판서 및 언어", "max_score": 15},
        "teaching_attitude": {"name": "수업 태도", "max_score": 15},
        "student_engagement": {"name": "학생 참여", "max_score": 15},
        "time_management": {"name": "시간 배분", "max_score": 10},
        "creativity": {"name": "창의성", "max_score": 5}
    }
    
    # Grade thresholds
    GRADE_THRESHOLDS = {
        90: "A+",
        85: "A",
        80: "B+",
        75: "B",
        70: "C+",
        65: "C",
        60: "D+",
        55: "D",
        0: "F"
    }
    
    @classmethod
    def get_grade(cls, score: float) -> str:
        """Convert numeric score to letter grade"""
        for threshold, grade in sorted(cls.GRADE_THRESHOLDS.items(), reverse=True):
            if score >= threshold:
                return grade
        return "F"


settings = Settings()

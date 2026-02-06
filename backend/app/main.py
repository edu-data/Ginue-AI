"""
🚀 GAIM Lab v3.0 - FastAPI Main Application
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.api.v1 import router as api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 GAIM Lab v3.0 서버 시작")
    print(f"   API URL: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"   Debug: {settings.DEBUG}")
    
    # Ensure directories exist
    for dir_path in [settings.UPLOADS_DIR, settings.OUTPUT_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Shutdown
    print("👋 GAIM Lab v3.0 서버 종료")


# Create FastAPI app
app = FastAPI(
    title="GAIM Lab v3.0",
    description="GINUE AI Microteaching Lab - 차세대 AI 수업 분석 플랫폼",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads and outputs
if settings.UPLOADS_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")
if settings.OUTPUT_DIR.exists():
    app.mount("/output", StaticFiles(directory=str(settings.OUTPUT_DIR)), name="output")

# API Routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "GAIM Lab v3.0",
        "description": "GINUE AI Microteaching Lab",
        "version": "3.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "3.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

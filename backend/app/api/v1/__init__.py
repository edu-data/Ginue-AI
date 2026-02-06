"""
GAIM Lab v3.0 - API v1 Router
"""

from fastapi import APIRouter

from .analysis import router as analysis_router
from .chat import router as chat_router
from .websocket import router as websocket_router

router = APIRouter()

# Mount sub-routers
router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
router.include_router(chat_router, prefix="/chat", tags=["AI Coach"])
router.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])


@router.get("/status")
async def api_status():
    """API status check"""
    return {
        "api_version": "v1",
        "status": "operational",
        "features": [
            "video_analysis",
            "realtime_feedback",
            "ai_coach_chat",
            "emotion_detection",
            "portfolio"
        ]
    }

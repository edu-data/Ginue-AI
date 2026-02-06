"""
📊 GAIM Lab v3.0 - Analysis API Endpoints
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()

# In-memory analysis store (use Redis/DB in production)
analysis_store = {}


class AnalysisRequest(BaseModel):
    """Analysis request model"""
    video_id: str
    options: Optional[dict] = None


class AnalysisResponse(BaseModel):
    """Analysis response model"""
    id: str
    status: str
    video_name: str
    created_at: str
    progress: int = 0
    result: Optional[dict] = None


class BatchAnalysisRequest(BaseModel):
    """Batch analysis request"""
    video_ids: List[str]


# ============================================================
# Upload Endpoints
# ============================================================

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file for analysis
    
    - **file**: Video file (MP4, AVI, MOV, MKV)
    """
    # Validate file type
    allowed_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {allowed_extensions}"
        )
    
    # Check file size
    max_size = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
    contents = await file.read()
    
    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_VIDEO_SIZE_MB}MB"
        )
    
    # Generate unique ID
    video_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{video_id}{file_ext}"
    
    # Save file
    file_path = settings.UPLOADS_DIR / filename
    settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Store metadata
    analysis_store[video_id] = {
        "id": video_id,
        "status": "uploaded",
        "video_name": file.filename,
        "file_path": str(file_path),
        "created_at": datetime.now().isoformat(),
        "progress": 0,
        "result": None
    }
    
    return {
        "id": video_id,
        "filename": filename,
        "size_mb": round(len(contents) / (1024 * 1024), 2),
        "message": "Upload successful"
    }


# ============================================================
# Analysis Endpoints
# ============================================================

@router.post("/analyze")
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Start video analysis
    
    - **video_id**: ID from upload response
    - **options**: Analysis options (optional)
    """
    if request.video_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Video not found")
    
    analysis = analysis_store[request.video_id]
    
    if analysis["status"] == "analyzing":
        raise HTTPException(status_code=400, detail="Analysis already in progress")
    
    # Update status
    analysis["status"] = "analyzing"
    analysis["progress"] = 5
    
    # Start background analysis
    background_tasks.add_task(
        run_analysis_pipeline,
        request.video_id,
        request.options or {}
    )
    
    return {
        "id": request.video_id,
        "status": "analyzing",
        "message": "Analysis started"
    }


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Get analysis result
    
    - **analysis_id**: Analysis ID
    """
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_store[analysis_id]


@router.get("/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """Get analysis status only"""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_store[analysis_id]
    return {
        "id": analysis_id,
        "status": analysis["status"],
        "progress": analysis["progress"]
    }


# ============================================================
# Batch Analysis Endpoints
# ============================================================

@router.get("/batch/videos")
async def list_available_videos():
    """List all uploaded videos available for batch analysis"""
    videos = []
    
    for video_id, data in analysis_store.items():
        videos.append({
            "id": video_id,
            "name": data["video_name"],
            "status": data["status"],
            "created_at": data["created_at"]
        })
    
    return {"videos": videos, "count": len(videos)}


@router.post("/batch/start")
async def start_batch_analysis(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Start batch analysis for multiple videos"""
    batch_id = str(uuid.uuid4())[:8]
    
    # Validate all video IDs exist
    for vid in request.video_ids:
        if vid not in analysis_store:
            raise HTTPException(
                status_code=404, 
                detail=f"Video {vid} not found"
            )
    
    # Start batch in background
    background_tasks.add_task(
        run_batch_analysis,
        batch_id,
        request.video_ids
    )
    
    return {
        "batch_id": batch_id,
        "video_count": len(request.video_ids),
        "status": "started"
    }


# ============================================================
# Background Tasks
# ============================================================

async def run_analysis_pipeline(video_id: str, options: dict):
    """
    Run the full analysis pipeline
    
    This is called as a background task
    """
    import sys
    sys.path.insert(0, str(settings.PROJECT_ROOT))
    
    analysis = analysis_store[video_id]
    
    try:
        from core.analyzers import TurboAnalyzer, FasterWhisperSTT, EmotionDetector
        
        video_path = Path(analysis["file_path"])
        output_dir = settings.OUTPUT_DIR / f"analysis_{video_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Phase 1: Video analysis (30%)
        analysis["progress"] = 10
        analyzer = TurboAnalyzer(temp_dir=str(output_dir / "cache"))
        vision_results, content_results = analyzer.analyze_video(video_path)
        analysis["progress"] = 30
        
        # Phase 2: STT (50%)
        analysis["progress"] = 35
        stt = FasterWhisperSTT(
            model_size=settings.WHISPER_MODEL,
            language=settings.WHISPER_LANGUAGE
        )
        transcript = stt.transcribe_video(str(video_path))
        analysis["progress"] = 50
        
        # Phase 3: Emotion detection (70%)
        analysis["progress"] = 55
        emotion = EmotionDetector()
        frames_dir = output_dir / "cache" / "frames"
        audio_path = output_dir / "cache" / "audio.wav"
        
        emotion_result = emotion.analyze_classroom_mood(
            str(frames_dir) if frames_dir.exists() else None,
            str(audio_path) if audio_path.exists() else None
        )
        analysis["progress"] = 70
        
        # Phase 4: Evaluation (90%)
        analysis["progress"] = 75
        evaluation = generate_evaluation(
            vision_results,
            content_results,
            transcript,
            emotion_result,
            analyzer.get_audio_metrics()
        )
        analysis["progress"] = 90
        
        # Store result
        analysis["result"] = {
            "evaluation": evaluation,
            "transcript": {
                "text": transcript.text,
                "segments_count": len(transcript.segments),
                "filler_words": transcript.filler_words
            },
            "emotion": emotion_result.get("summary", {}),
            "vision": analyzer.get_vision_summary(),
            "audio": analyzer.get_audio_metrics()
        }
        
        analysis["status"] = "completed"
        analysis["progress"] = 100
        
    except Exception as e:
        analysis["status"] = "failed"
        analysis["error"] = str(e)
        print(f"❌ Analysis failed: {e}")


async def run_batch_analysis(batch_id: str, video_ids: List[str]):
    """Run batch analysis for multiple videos"""
    for i, vid in enumerate(video_ids):
        await run_analysis_pipeline(vid, {})


def generate_evaluation(
    vision_results: list,
    content_results: list,
    transcript,
    emotion_result: dict,
    audio_metrics: dict
) -> dict:
    """Generate 7-dimension evaluation from analysis results"""
    
    # Calculate metrics
    face_ratio = 0.7 if vision_results else 0.3
    gesture_ratio = sum(1 for v in vision_results if v.get("gesture_active", False)) / max(len(vision_results), 1)
    positive_ratio = emotion_result.get("summary", {}).get("positive_ratio", 0.5)
    filler_count = sum(transcript.filler_words.values()) if transcript else 0
    
    # Heuristic scoring (simplified)
    dimensions = {
        "teaching_expertise": {
            "score": min(16, 10 + (len(transcript.text) // 500) if transcript else 10),
            "max_score": 20,
            "feedback": "학습 목표가 명확하게 제시되었습니다."
        },
        "teaching_method": {
            "score": min(16, 12 + int(gesture_ratio * 10)),
            "max_score": 20,
            "feedback": "다양한 교수법을 활용하고 있습니다."
        },
        "communication": {
            "score": max(8, 15 - filler_count // 5),
            "max_score": 15,
            "feedback": f"습관어 {filler_count}회 감지됨. 발화 명료성을 높여보세요."
        },
        "teaching_attitude": {
            "score": min(12, 8 + int(positive_ratio * 10)),
            "max_score": 15,
            "feedback": "자신감 있는 수업 태도가 돋보입니다."
        },
        "student_engagement": {
            "score": 10,
            "max_score": 15,
            "feedback": "학생 상호작용 증가를 권장합니다."
        },
        "time_management": {
            "score": 7,
            "max_score": 10,
            "feedback": "시간 배분이 적절합니다."
        },
        "creativity": {
            "score": 3,
            "max_score": 5,
            "feedback": "창의적인 교수법 시도가 필요합니다."
        }
    }
    
    total_score = sum(d["score"] for d in dimensions.values())
    
    # Grade
    if total_score >= 90:
        grade = "A+"
    elif total_score >= 85:
        grade = "A"
    elif total_score >= 80:
        grade = "B+"
    elif total_score >= 75:
        grade = "B"
    elif total_score >= 70:
        grade = "C+"
    elif total_score >= 65:
        grade = "C"
    else:
        grade = "D"
    
    return {
        "total_score": total_score,
        "grade": grade,
        "dimensions": dimensions
    }

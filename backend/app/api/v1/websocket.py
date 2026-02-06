"""
🔌 GAIM Lab v3.0 - WebSocket API
실시간 분석 피드백 및 스트리밍
"""

from typing import Dict, Set
from datetime import datetime
import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Active connections store
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str):
        """Accept and store connection"""
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        
        self.active_connections[channel].add(websocket)
        print(f"🔌 WebSocket connected: {channel}")
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove connection"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        
        print(f"🔌 WebSocket disconnected: {channel}")
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"WebSocket send error: {e}")
    
    async def broadcast(self, channel: str, message: dict):
        """Broadcast message to all connections in a channel"""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected
        for conn in disconnected:
            self.active_connections[channel].discard(conn)


manager = ConnectionManager()


# ============================================================
# Analysis Progress WebSocket
# ============================================================

@router.websocket("/analysis/{analysis_id}")
async def analysis_websocket(websocket: WebSocket, analysis_id: str):
    """
    WebSocket for real-time analysis progress
    
    Messages:
    - type: "progress" - Analysis progress update
    - type: "complete" - Analysis completed
    - type: "error" - Analysis error
    """
    channel = f"analysis:{analysis_id}"
    await manager.connect(websocket, channel)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
            except json.JSONDecodeError:
                pass
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


# ============================================================
# Real-time Feedback WebSocket
# ============================================================

@router.websocket("/realtime")
async def realtime_feedback_websocket(websocket: WebSocket):
    """
    WebSocket for real-time camera streaming feedback
    
    Client sends:
    - type: "frame" - Video frame data (base64)
    - type: "audio" - Audio chunk data (base64)
    
    Server sends:
    - type: "feedback" - Real-time analysis feedback
    - type: "score" - Current evaluation scores
    """
    channel = f"realtime:{datetime.now().strftime('%H%M%S')}"
    await manager.connect(websocket, channel)
    
    try:
        await manager.send_personal(websocket, {
            "type": "connected",
            "message": "Real-time feedback ready",
            "timestamp": datetime.now().isoformat()
        })
        
        frame_count = 0
        
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "frame":
                    frame_count += 1
                    
                    # Analyze frame (simplified)
                    feedback = analyze_frame_realtime(message.get("data"))
                    
                    await manager.send_personal(websocket, {
                        "type": "feedback",
                        "frame_number": frame_count,
                        "feedback": feedback,
                        "timestamp": datetime.now().isoformat()
                    })
                
                elif msg_type == "audio":
                    # Analyze audio chunk
                    audio_feedback = analyze_audio_realtime(message.get("data"))
                    
                    await manager.send_personal(websocket, {
                        "type": "audio_feedback",
                        "feedback": audio_feedback,
                        "timestamp": datetime.now().isoformat()
                    })
                
                elif msg_type == "stop":
                    # Generate final summary
                    await manager.send_personal(websocket, {
                        "type": "summary",
                        "frames_processed": frame_count,
                        "message": "Real-time session ended",
                        "timestamp": datetime.now().isoformat()
                    })
                    break
                
            except json.JSONDecodeError:
                pass
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


# ============================================================
# Helper Functions for Real-time Analysis
# ============================================================

def analyze_frame_realtime(frame_data: str) -> dict:
    """
    Analyze a single frame for real-time feedback
    
    Returns lightweight feedback for immediate display
    """
    # Simplified analysis (in production, use actual vision models)
    return {
        "face_visible": True,
        "eye_contact": True,
        "gesture_detected": False,
        "posture": "good",
        "tips": []
    }


def analyze_audio_realtime(audio_data: str) -> dict:
    """
    Analyze audio chunk for real-time feedback
    """
    return {
        "volume": "normal",
        "pace": "appropriate",
        "filler_detected": False
    }


# ============================================================
# Utility: Broadcast Progress Updates
# ============================================================

async def broadcast_progress(analysis_id: str, progress: int, message: str):
    """
    Broadcast analysis progress to connected clients
    
    Call this from analysis pipeline
    """
    channel = f"analysis:{analysis_id}"
    
    await manager.broadcast(channel, {
        "type": "progress",
        "progress": progress,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_complete(analysis_id: str, result: dict):
    """Broadcast analysis completion"""
    channel = f"analysis:{analysis_id}"
    
    await manager.broadcast(channel, {
        "type": "complete",
        "result": result,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_error(analysis_id: str, error: str):
    """Broadcast analysis error"""
    channel = f"analysis:{analysis_id}"
    
    await manager.broadcast(channel, {
        "type": "error",
        "error": error,
        "timestamp": datetime.now().isoformat()
    })

"""
🤖 GAIM Lab v3.0 - AI Coach Chat API
Gemini 기반 대화형 수업 코칭
"""

import os
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Chat history store (use Redis/DB in production)
chat_sessions = {}


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request model"""
    session_id: Optional[str] = None
    message: str
    analysis_id: Optional[str] = None  # Link to analysis result


class ChatResponse(BaseModel):
    """Chat response model"""
    session_id: str
    message: ChatMessage
    suggestions: List[str] = []


# System prompt for AI Coach
COACH_SYSTEM_PROMPT = """당신은 GAIM Lab의 'AI 수업 코치'입니다. 
예비교사들의 수업 역량 향상을 돕는 전문 코칭 AI입니다.

역할:
1. 7차원 평가 결과(수업 전문성, 교수학습 방법, 판서 및 언어, 수업 태도, 학생 참여, 시간 배분, 창의성)에 대해 상세히 설명합니다.
2. 개선점에 대한 구체적이고 실행 가능한 조언을 제공합니다.
3. 교육학 이론과 연구 결과를 근거로 피드백합니다.
4. 격려하고 긍정적인 톤을 유지합니다.
5. 질문에 친절하고 전문적으로 답변합니다.

규칙:
- 한국어로 답변합니다.
- 답변은 명확하고 구조화되어야 합니다.
- 필요시 예시를 들어 설명합니다.
- 교육학 용어를 사용할 때는 쉽게 풀어서 설명합니다.
"""


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to AI Coach
    
    - **message**: User's question or request
    - **session_id**: Chat session ID (optional, auto-generated if not provided)
    - **analysis_id**: Link to analysis result for context (optional)
    """
    if not GEMINI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI Coach not available. Please install google-generativeai."
        )
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_API_KEY not configured"
        )
    
    # Get or create session
    session_id = request.session_id or datetime.now().strftime("%Y%m%d%H%M%S")
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            "messages": [],
            "analysis_id": request.analysis_id,
            "created_at": datetime.now().isoformat()
        }
    
    session = chat_sessions[session_id]
    
    # Add user message
    user_msg = ChatMessage(
        role="user",
        content=request.message,
        timestamp=datetime.now().isoformat()
    )
    session["messages"].append(user_msg.dict())
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Build conversation history
        history_text = COACH_SYSTEM_PROMPT + "\n\n"
        for msg in session["messages"][-10:]:  # Last 10 messages
            role = "사용자" if msg["role"] == "user" else "AI 코치"
            history_text += f"{role}: {msg['content']}\n\n"
        
        # Generate response
        response = model.generate_content(history_text)
        assistant_content = response.text
        
        # Add assistant message
        assistant_msg = ChatMessage(
            role="assistant",
            content=assistant_content,
            timestamp=datetime.now().isoformat()
        )
        session["messages"].append(assistant_msg.dict())
        
        # Generate follow-up suggestions
        suggestions = generate_suggestions(request.message, assistant_content)
        
        return ChatResponse(
            session_id=session_id,
            message=assistant_msg,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Coach error: {str(e)}"
        )


@router.get("/session/{session_id}")
async def get_chat_session(session_id: str):
    """Get chat session history"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return chat_sessions[session_id]


@router.delete("/session/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete chat session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del chat_sessions[session_id]
    return {"message": "Session deleted"}


@router.post("/quick-feedback")
async def quick_feedback(analysis_id: str):
    """
    Generate quick feedback based on analysis result
    
    Returns AI-generated improvement tips
    """
    # This would integrate with analysis results
    # For now, return sample tips
    
    tips = [
        "💡 발문 기법을 개선해 보세요. 개방형 질문을 더 많이 활용하면 학생 참여가 높아집니다.",
        "📝 판서할 때 글씨 크기를 조금 더 키우면 가독성이 향상됩니다.",
        "⏱️ 도입 단계에서 전시학습 상기를 간략하게 하면 본시 학습 시간을 확보할 수 있습니다.",
        "👀 교실 전체를 고르게 바라보며 시선을 분산시켜 보세요.",
        "🎭 긍정적인 표정과 제스처를 더 적극적으로 활용해 보세요."
    ]
    
    return {
        "analysis_id": analysis_id,
        "tips": tips
    }


def generate_suggestions(user_message: str, ai_response: str) -> List[str]:
    """Generate follow-up question suggestions"""
    
    # Simple keyword-based suggestions
    suggestions = []
    
    keywords = {
        "발문": ["효과적인 발문 예시를 알려주세요", "개방형 질문과 폐쇄형 질문의 차이점은?"],
        "시선": ["아이컨택 연습 방법을 알려주세요", "교실 시선 분배 팁을 알려주세요"],
        "습관어": ["습관어를 줄이는 방법은?", "말하기 연습은 어떻게 하나요?"],
        "시간": ["수업 시간 배분 가이드를 알려주세요", "도입-전개-정리 비율은?"],
        "학생": ["학생 참여를 높이는 방법은?", "소극적인 학생을 어떻게 참여시키나요?"]
    }
    
    for keyword, related in keywords.items():
        if keyword in user_message or keyword in ai_response:
            suggestions.extend(related[:1])
    
    # Default suggestions
    if not suggestions:
        suggestions = [
            "수업 전문성을 높이려면 어떻게 해야 하나요?",
            "다음 수업에서 바로 적용할 수 있는 팁을 알려주세요"
        ]
    
    return suggestions[:3]

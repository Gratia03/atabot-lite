from fastapi import APIRouter, HTTPException
from typing import List

from app.models.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.chatbot_service import ChatbotService
from app.schemas.common import DataResponse

router = APIRouter()

# Initialize chatbot service
chatbot_service = ChatbotService()

async def initialize_chatbot_embeddings():
    """Initialize embeddings on startup"""
    await chatbot_service.initialize_embeddings()

@router.post("/message", response_model=DataResponse[ChatResponse])
async def send_message(request: ChatRequest):
    """Send message to chatbot and get response"""
    try:
        response = await chatbot_service.process_message(request)
        
        return DataResponse(
            success=True,
            message="Message processed successfully",
            data=response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}", response_model=DataResponse[List[ChatMessage]])
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    history = chatbot_service.get_session_history(session_id)
    
    return DataResponse(
        success=True,
        message="History retrieved successfully",
        data=history
    )

@router.delete("/session/{session_id}", response_model=DataResponse[None])
async def clear_session(session_id: str):
    """Clear a chat session"""
    chatbot_service.clear_session(session_id)
    
    return DataResponse(
        success=True,
        message="Session cleared successfully",
        data=None
    )

@router.post("/reload", response_model=DataResponse[None])
async def reload_data():
    """Reload chatbot configuration and data"""
    try:
        chatbot_service._load_data()
        await chatbot_service.initialize_embeddings()
        
        return DataResponse(
            success=True,
            message="Data reloaded successfully",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
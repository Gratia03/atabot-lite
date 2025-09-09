from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, AsyncGenerator
import json

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
        # Ensure session_id is provided or generated
        if not request.session_id:
            import uuid
            request.session_id = str(uuid.uuid4())
        
        response = await chatbot_service.process_message(request)
        
        return DataResponse(
            success=True,
            message="Message processed successfully",
            data=response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message/stream")
async def send_message_stream(request: ChatRequest):
    """Send message to chatbot and get streaming response"""
    try:
        # Ensure session_id is provided or generated
        if not request.session_id:
            import uuid
            request.session_id = str(uuid.uuid4())
        
        async def generate() -> AsyncGenerator[str, None]:
            # Process message with streaming
            async for chunk in chatbot_service.process_message_stream(request):
                # Format as Server-Sent Event
                data = json.dumps({
                    "type": chunk.get("type", "content"),
                    "content": chunk.get("content", ""),
                    "session_id": chunk.get("session_id", request.session_id),
                    "done": chunk.get("done", False)
                })
                yield f"data: {data}\n\n"
                
            # Send final message
            yield f"data: {json.dumps({'type': 'done', 'done': True})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable proxy buffering
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/create", response_model=DataResponse[dict])
async def create_session():
    """Create a new chat session"""
    import uuid
    session_id = str(uuid.uuid4())
    
    # Initialize session in service
    chatbot_service.create_session(session_id)
    
    return DataResponse(
        success=True,
        message="Session created successfully",
        data={"session_id": session_id}
    )

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
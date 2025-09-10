import time
from fastapi import Request
from app.services.analytics_service import analytics_service

async def analytics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Track response time for chat endpoints
    if "/chat/message" in str(request.url):
        response_time = time.time() - start_time
        # Extract session_id and message from request (simplified)
        # In real implementation, you'd need proper extraction logic
        await analytics_service.track_message("session", "message", response_time)
    
    return response
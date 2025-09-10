from fastapi import APIRouter, Depends, HTTPException
from app.schemas.common import DataResponse
from app.services.analytics_service import analytics_service
from app.api.v1.endpoints.admin import verify_admin

router = APIRouter()

@router.get("/stats", response_model=DataResponse[dict])
async def get_analytics_stats(admin = Depends(verify_admin)):
    """Get analytics statistics"""
    stats = analytics_service.get_stats()
    return DataResponse(
        success=True,
        message="Analytics retrieved successfully",
        data=stats
    )

@router.post("/feedback")
async def submit_feedback(
    session_id: str,
    rating: int,
    feedback: str = ""
):
    """Submit user feedback"""
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1-5")
    
    await analytics_service.add_user_feedback(session_id, rating, feedback)
    
    return DataResponse(
        success=True,
        message="Feedback submitted successfully",
        data=None
    )

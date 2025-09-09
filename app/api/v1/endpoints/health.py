from fastapi import APIRouter
from app.schemas.common import ResponseBase

router = APIRouter()

@router.get("/", response_model=ResponseBase)
async def health_check():
    """Health check endpoint"""
    return ResponseBase(
        success=True,
        message="Atabot-Lite is running"
    )
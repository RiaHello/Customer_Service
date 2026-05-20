"""Health Check Route"""
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    version: str


class APIResponse(BaseModel):
    """Standard API response"""
    code: int
    message: str
    data: HealthResponse


@router.get("/health", response_model=APIResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        APIResponse: Health status with timestamp and version
    """
    return {
        "code": 200,
        "message": "success",
        "data": {
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0.0"
        }
    }

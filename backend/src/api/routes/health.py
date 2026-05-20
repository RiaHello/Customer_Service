"""Health Check Route"""
from datetime import datetime

from fastapi.responses import JSONResponse

from pycore.api import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    健康检查接口

    Returns:
        统一响应格式，包含健康状态、时间戳和版本信息
    """
    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0.0",
        },
    }
    return JSONResponse(content=response_data, status_code=200)

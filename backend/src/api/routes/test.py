"""
Test Route Handler - 用于验证 JWT 中间件的测试端点

⚠️ 此文件仅用于测试 JWT 认证功能，不属于业务逻辑。
"""
from fastapi import APIRouter, Depends

from src.api.deps import get_current_user

router = APIRouter(prefix="/api", tags=["test"])


@router.get("/test")
async def protected_test(current_user: dict = Depends(get_current_user)):
    """
    受保护的测试端点

    用于验证 JWT 中间件是否正确拦截未认证请求，并允许有效 Token 访问。

    Returns:
        dict: 包含成功消息和当前用户信息
    """
    return {
        "code": 200,
        "message": "success",
        "data": {
            "message": "Protected endpoint accessed successfully",
            "user": current_user,
        },
    }

"""
Auth Route Handler - 认证相关路由

包含登录、注册等认证接口。
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login_placeholder():
    """
    登录端点占位符

    ⚠️ 此为占位实现，完整登录逻辑将在 T-010（用户登录接口）中实现。

    当前仅用于：
    - 验证中间件白名单功能（/api/auth/login 应无需 Token 可访问）
    - 确保路由注册正确

    Returns:
        dict: 占位响应消息
    """
    return {
        "code": 200,
        "message": "Login endpoint placeholder - will be implemented in T-010",
        "data": None,
    }

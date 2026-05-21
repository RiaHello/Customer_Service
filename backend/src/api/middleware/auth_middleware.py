"""
认证中间件

拦截所有 /api/* 请求（除免认证路由），验证 JWT Token。
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from pycore.core import get_logger
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.auth import verify_token

logger = get_logger()

# 免认证路径白名单
WHITELIST_PATHS = {
    "/health",
    "/api/auth/login",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT Token 认证中间件"""

    async def dispatch(self, request: Request, call_next):
        """
        拦截请求，验证 JWT Token

        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器

        Returns:
            Response: 响应对象
        """
        path = request.url.path

        # 放行 OPTIONS 预检请求
        if request.method == "OPTIONS":
            return await call_next(request)

        # 白名单路径直接放行
        if path in WHITELIST_PATHS:
            return await call_next(request)

        # 非 /api/* 路径直接放行
        if not path.startswith("/api/"):
            return await call_next(request)

        # 提取 Authorization 头
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            logger.warning("Missing Authorization header", path=path)
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": "Unauthorized", "data": None},
            )

        # 验证 Bearer Token 格式
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning("Invalid Authorization header format", path=path)
            return JSONResponse(
                status_code=401,
                content={
                    "code": 401,
                    "message": "Invalid Authorization header",
                    "data": None,
                },
            )

        token = parts[1]

        # 验证 Token
        try:
            user_info = verify_token(token)
            # 将用户信息注入请求状态，供后续处理器使用
            request.state.user = user_info
            logger.debug(
                "Request authenticated",
                path=path,
                user_id=user_info["user_id"],
                username=user_info["username"],
            )
        except ValueError as e:
            error_msg = str(e)
            if "expired" in error_msg.lower():
                logger.warning("Token expired", path=path)
                return JSONResponse(
                    status_code=401,
                    content={"code": 401, "message": "Token expired", "data": None},
                )
            else:
                logger.warning("Invalid token", path=path, error=error_msg)
                return JSONResponse(
                    status_code=401,
                    content={"code": 401, "message": "Invalid token", "data": None},
                )

        # Token 验证通过，继续处理请求
        return await call_next(request)

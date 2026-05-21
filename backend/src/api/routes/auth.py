"""
Auth Route Handler - 认证相关路由

包含登录、注册等认证接口。
"""
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pycore.core import get_logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.auth import create_access_token
from src.core.config import settings
from src.core.responses import success_response
from src.core.security import verify_password
from src.models.auth import LoginRequest, LoginResponse, UserInfo

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = get_logger()


@router.post("/login", response_model=None)
async def login(request: LoginRequest):
    """
    用户登录

    根据用户名和密码验证用户身份，成功后返回 JWT Token 和用户信息。

    Args:
        request: 登录请求 {"username": "...", "password": "..."}

    Returns:
        登录响应 {"code": 200, "message": "登录成功", "data": {"access_token": "...", "token_type": "Bearer", "user": {...}}}

    Raises:
        400: 用户名或密码错误
        500: 数据库错误
    """
    try:
        # 1. 创建数据库连接（使用异步引擎）
        engine = create_async_engine(
            settings.database_url,
            echo=False,
            future=True,
        )

        async with engine.begin() as conn:
            # 2. 查询用户
            result = await conn.execute(
                text("SELECT id, username, password_hash, role, nickname, created_at FROM users WHERE username = :username"),
                {"username": request.username},
            )
            user_row = result.fetchone()

        # 关闭引擎
        await engine.dispose()

        # 3. 验证用户存在
        if not user_row:
            logger.warning("Login failed: user not found", username=request.username)
            return JSONResponse(
                status_code=401,
                content={
                    "code": 1001,
                    "message": "用户名或密码错误",
                    "data": None,
                },
            )

        user_id, username, password_hash, role, nickname, created_at = user_row

        # 4. 验证密码
        if not verify_password(request.password, password_hash):
            logger.warning("Login failed: incorrect password", username=request.username)
            return JSONResponse(
                status_code=401,
                content={
                    "code": 1001,
                    "message": "用户名或密码错误",
                    "data": None,
                },
            )

        # 5. 生成 Token
        access_token = create_access_token(
            user_id=user_id,
            username=username,
            role=role,
        )

        # 6. 构造用户信息
        display_name = nickname if nickname else username

        # 格式化时间戳（如果是 datetime 对象）
        if isinstance(created_at, datetime):
            created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # SQLite 返回的可能是字符串
            created_at_str = str(created_at)

        user_info = UserInfo(
            user_id=user_id,
            username=username,
            role=role,
            display_name=display_name,
            created_at=created_at_str,
        )

        # 7. 构造响应数据
        login_response = LoginResponse(
            token=access_token,
            token_type="Bearer",
            user=user_info,
        )

        logger.info("Login successful", user_id=user_id, username=username, role=role)

        # 8. 返回成功响应
        return success_response(data=login_response.model_dump(), message="success")

    except Exception as e:
        logger.error("Login error", error=str(e), username=request.username)
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "data": None,
            },
        )

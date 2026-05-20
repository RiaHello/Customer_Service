"""
JWT Token 认证模块

提供 JWT Token 的生成与验证功能。
"""
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from pycore.core import get_logger
from src.core.config import settings

logger = get_logger()


def create_access_token(
    user_id: int, username: str, role: str, expires_delta: timedelta | None = None
) -> str:
    """
    创建 JWT Access Token

    Args:
        user_id: 用户 ID
        username: 用户名
        role: 用户角色
        expires_delta: 过期时间增量（可选）

    Returns:
        str: JWT Token 字符串
    """
    # Token 有效载荷
    to_encode: dict[str, Any] = {
        "sub": str(user_id),  # subject: 用户 ID (转为字符串)
        "username": username,
        "role": role,
    }

    # 计算过期时间
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    to_encode["exp"] = expire

    # 生成 JWT Token
    encoded_jwt: str = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )

    logger.info(
        "JWT Token created",
        user_id=user_id,
        username=username,
        role=role,
        expires_at=expire.isoformat(),
    )

    return encoded_jwt


def verify_token(token: str) -> dict[str, Any]:
    """
    验证 JWT Token

    Args:
        token: JWT Token 字符串

    Returns:
        dict: Token 载荷（包含 sub, username, role）

    Raises:
        ValueError: Token 无效或过期
    """
    try:
        # 解码并验证 Token
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )

        # 提取用户信息
        user_id = payload.get("sub")
        username = payload.get("username")
        role = payload.get("role")

        if user_id is None or username is None or role is None:
            raise ValueError("Invalid token: missing required claims")

        logger.debug("JWT Token verified", user_id=user_id, username=username, role=role)

        return {
            "user_id": int(user_id),  # 转回整数
            "username": username,
            "role": role,
        }

    except JWTError as e:
        # JWT 解码错误（无效签名、格式错误等）
        error_msg = str(e)
        if "expired" in error_msg.lower():
            logger.warning("JWT Token expired", error=error_msg)
            raise ValueError("Token expired") from None
        else:
            logger.warning("JWT Token invalid", error=error_msg)
            raise ValueError("Invalid token") from None

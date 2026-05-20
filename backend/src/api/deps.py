"""
API Dependencies - FastAPI 依赖注入函数

提供常用的依赖项（如数据库会话、当前用户等）。
"""
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request


# 当前用户依赖
def get_current_user(request: Request) -> dict[str, Any]:
    """
    获取当前认证用户信息（依赖注入）

    从请求状态中提取用户信息（由认证中间件注入）。

    Args:
        request: FastAPI 请求对象

    Returns:
        dict: 用户信息（包含 user_id, username, role）

    Raises:
        HTTPException: 如果用户信息不存在（不应发生，因为中间件已验证）
    """
    # 认证中间件已将用户信息注入到 request.state.user
    user_info: dict[str, Any] | None = getattr(request.state, "user", None)

    if user_info is None:
        # 理论上不应到达这里，因为中间件已经验证过
        # 如果到达这里，说明中间件配置有问题
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user_info


# 类型别名：当前用户依赖
CurrentUser = Annotated[dict[str, Any], Depends(get_current_user)]

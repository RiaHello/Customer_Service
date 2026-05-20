"""统一响应格式（符合 API 契约）"""
from typing import Any


def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200,
) -> dict[str, Any]:
    """
    创建成功响应（符合 API 契约格式）。

    Args:
        data: 响应数据
        message: 响应消息
        code: 响应码

    Returns:
        {"code": 200, "message": "success", "data": {...}}
    """
    return {
        "code": code,
        "message": message,
        "data": data,
    }


def error_response(
    message: str,
    code: int = 400,
    data: Any = None,
) -> dict[str, Any]:
    """
    创建错误响应（符合 API 契约格式）。

    Args:
        message: 错误消息
        code: 错误码
        data: 可选的错误详情

    Returns:
        {"code": <code>, "message": "<message>", "data": null}
    """
    return {
        "code": code,
        "message": message,
        "data": data,
    }

"""
WebSocket 路由

实现 WebSocket 实时消息推送。
"""
from datetime import UTC, datetime

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from pycore.core import get_logger

from src.core.auth import verify_token
from src.core.websocket_pool import get_websocket_pool

logger = get_logger()

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/tickets/{ticket_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    ticket_id: int,
    token: str = Query(..., description="JWT access_token (不带 Bearer 前缀)"),
) -> None:
    """
    WebSocket 工单实时消息连接

    Args:
        websocket: WebSocket 连接实例
        ticket_id: 工单 ID
        token: JWT Token（Query 参数）
    """
    pool = get_websocket_pool()

    # 1. 验证 Token
    try:
        user_info = verify_token(token)
        logger.info(
            "WebSocket connection request",
            ticket_id=ticket_id,
            user_id=user_info["user_id"],
            username=user_info["username"],
        )
    except ValueError as e:
        # Token 无效，拒绝连接
        logger.warning(
            "WebSocket connection rejected: invalid token",
            ticket_id=ticket_id,
            error=str(e),
        )
        await websocket.close(code=1008, reason="Invalid token")
        return

    # 2. 接受连接
    await websocket.accept()
    logger.info(
        "WebSocket connection accepted",
        ticket_id=ticket_id,
        user_id=user_info["user_id"],
    )

    # 3. 注册到连接池
    pool.register(ticket_id, websocket)

    # 4. 发送 connected 消息
    connected_message = {
        "type": "connected",
        "data": {
            "ticket_id": ticket_id,
            "message": "WebSocket连接成功",
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        },
    }
    await pool.send_to_connection(websocket, connected_message)

    # 5. 启动心跳
    await pool.start_heartbeat(websocket, interval=30)

    # 6. 接收消息循环
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            message_type = data.get("type")

            # 处理客户端 ping 消息
            if message_type == "ping":
                # 回复 pong
                pong_message = {
                    "type": "pong",
                    "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                }
                await pool.send_to_connection(websocket, pong_message)
                logger.debug(
                    "Received ping, sent pong",
                    ticket_id=ticket_id,
                    user_id=user_info["user_id"],
                )
            elif message_type == "pong":
                # 更新最后 pong 时间
                pool.update_pong_time(websocket)
                logger.debug(
                    "Received pong, updated pong time",
                    ticket_id=ticket_id,
                    user_id=user_info["user_id"],
                )
            else:
                # 其他消息类型暂时只记录日志
                logger.info(
                    "Received WebSocket message",
                    ticket_id=ticket_id,
                    message_type=message_type,
                    user_id=user_info["user_id"],
                )

    except WebSocketDisconnect:
        logger.info(
            "WebSocket disconnected (normal)",
            ticket_id=ticket_id,
            user_id=user_info["user_id"],
        )
    except Exception as e:
        logger.error(
            "WebSocket error",
            ticket_id=ticket_id,
            user_id=user_info["user_id"],
            error=str(e),
        )
    finally:
        # 7. 连接关闭时注销
        pool.unregister(websocket)
        logger.info(
            "WebSocket connection closed",
            ticket_id=ticket_id,
            user_id=user_info["user_id"],
        )

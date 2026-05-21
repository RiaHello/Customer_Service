"""
WebSocket 连接池管理

管理 WebSocket 连接的注册、注销、广播和心跳检测。
"""
import asyncio
import time
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from fastapi import WebSocket
from pycore.core import get_logger

logger = get_logger()


class WebSocketPool:
    """WebSocket 连接池"""

    def __init__(self) -> None:
        """初始化连接池"""
        # ticket_id -> list of WebSocket connections
        self._connections: dict[int, list[WebSocket]] = defaultdict(list)
        # WebSocket -> ticket_id mapping (for quick lookup on disconnect)
        self._ws_to_ticket: dict[WebSocket, int] = {}
        # WebSocket -> heartbeat task mapping
        self._heartbeat_tasks: dict[WebSocket, asyncio.Task] = {}
        # WebSocket -> last pong time mapping (for timeout detection)
        self._last_pong_time: dict[WebSocket, float] = {}
        logger.info("WebSocketPool initialized")

    def register(self, ticket_id: int, websocket: WebSocket) -> None:
        """
        注册 WebSocket 连接

        Args:
            ticket_id: 工单 ID
            websocket: WebSocket 连接实例
        """
        self._connections[ticket_id].append(websocket)
        self._ws_to_ticket[websocket] = ticket_id
        logger.info(
            "WebSocket registered",
            ticket_id=ticket_id,
            total_connections=len(self._connections[ticket_id]),
        )

    def unregister(self, websocket: WebSocket) -> None:
        """
        注销 WebSocket 连接

        Args:
            websocket: WebSocket 连接实例
        """
        # 获取 ticket_id
        ticket_id = self._ws_to_ticket.pop(websocket, None)
        if ticket_id is None:
            logger.warning("Attempted to unregister unknown WebSocket")
            return

        # 从连接列表中移除
        if ticket_id in self._connections:
            try:
                self._connections[ticket_id].remove(websocket)
            except ValueError:
                pass  # 连接已经不在列表中

            # 如果该 ticket_id 没有连接了，清理字典
            if not self._connections[ticket_id]:
                del self._connections[ticket_id]

        # 取消心跳任务
        heartbeat_task = self._heartbeat_tasks.pop(websocket, None)
        if heartbeat_task and not heartbeat_task.done():
            heartbeat_task.cancel()

        # 清理 pong 时间记录
        self._last_pong_time.pop(websocket, None)

        logger.info(
            "WebSocket unregistered",
            ticket_id=ticket_id,
            remaining_connections=len(self._connections.get(ticket_id, [])),
        )

    async def broadcast(self, ticket_id: int, message: dict[str, Any]) -> None:
        """
        广播消息到指定 ticket_id 的所有连接

        Args:
            ticket_id: 工单 ID
            message: 消息内容（字典格式）
        """
        connections = self._connections.get(ticket_id, [])
        if not connections:
            logger.debug("No connections to broadcast", ticket_id=ticket_id)
            return

        logger.info(
            "Broadcasting message",
            ticket_id=ticket_id,
            message_type=message.get("type"),
            connection_count=len(connections),
        )

        # 并发发送给所有连接
        tasks = [
            self.send_to_connection(ws, message)
            for ws in connections
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def send_to_connection(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        """
        发送消息到单个连接

        Args:
            websocket: WebSocket 连接实例
            message: 消息内容（字典格式）
        """
        try:
            await websocket.send_json(message)
            logger.debug(
                "Message sent",
                message_type=message.get("type"),
            )
        except Exception as e:
            logger.error(
                "Failed to send message",
                message_type=message.get("type"),
                error=str(e),
            )
            # 连接异常时自动注销
            self.unregister(websocket)

    async def start_heartbeat(
        self, websocket: WebSocket, interval: int = 30, pong_timeout: int = 10
    ) -> None:
        """
        启动心跳检测

        Args:
            websocket: WebSocket 连接实例
            interval: 心跳间隔（秒）
            pong_timeout: pong 超时时间（秒）
        """
        # 心跳配置常量
        HEARTBEAT_INTERVAL = interval  # 心跳间隔
        PONG_TIMEOUT = pong_timeout  # pong 超时时间（秒）

        async def heartbeat_loop() -> None:
            """心跳循环，带超时检测"""
            # 初始化最后 pong 时间
            self._last_pong_time[websocket] = time.time()

            try:
                while True:
                    await asyncio.sleep(HEARTBEAT_INTERVAL)

                    # 检查上次 pong 是否超时
                    last_pong = self._last_pong_time.get(websocket, 0)
                    time_since_last_pong = time.time() - last_pong

                    if time_since_last_pong > HEARTBEAT_INTERVAL + PONG_TIMEOUT:
                        # 超时，关闭连接
                        logger.warning(
                            "Heartbeat timeout detected",
                            time_since_last_pong=time_since_last_pong,
                            timeout_threshold=HEARTBEAT_INTERVAL + PONG_TIMEOUT,
                        )
                        await websocket.close(code=1008, reason="Heartbeat timeout")
                        break

                    # 发送 ping 消息
                    ping_message = {
                        "type": "ping",
                        "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    await self.send_to_connection(websocket, ping_message)
                    logger.debug("Heartbeat ping sent")

            except asyncio.CancelledError:
                logger.debug("Heartbeat task cancelled")
            except Exception as e:
                logger.error("Heartbeat task error", error=str(e))
                self.unregister(websocket)
            finally:
                # 清理 pong 时间记录
                self._last_pong_time.pop(websocket, None)

        # 创建心跳任务
        task = asyncio.create_task(heartbeat_loop())
        self._heartbeat_tasks[websocket] = task
        logger.info(
            "Heartbeat task started", interval=interval, pong_timeout=pong_timeout
        )

    def get_connection_count(self, ticket_id: int) -> int:
        """
        获取指定工单的连接数

        Args:
            ticket_id: 工单 ID

        Returns:
            int: 连接数
        """
        return len(self._connections.get(ticket_id, []))

    def update_pong_time(self, websocket: WebSocket) -> None:
        """
        更新连接的最后 pong 时间

        Args:
            websocket: WebSocket 连接实例
        """
        if websocket in self._last_pong_time:
            self._last_pong_time[websocket] = time.time()
            logger.debug("Pong time updated")
        else:
            logger.warning("Attempted to update pong time for untracked WebSocket")


# 全局单例
_pool: WebSocketPool | None = None


def get_websocket_pool() -> WebSocketPool:
    """
    获取 WebSocket 连接池单例

    Returns:
        WebSocketPool: 连接池实例
    """
    global _pool
    if _pool is None:
        _pool = WebSocketPool()
    return _pool

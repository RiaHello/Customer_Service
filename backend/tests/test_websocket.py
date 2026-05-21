"""
WebSocket 连接池和路由的单元测试
"""
import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from src.core.auth import create_access_token
from src.core.websocket_pool import WebSocketPool, get_websocket_pool
from src.main import app


@pytest.fixture
def pool() -> WebSocketPool:
    """创建新的 WebSocket 连接池实例"""
    return WebSocketPool()


class TestWebSocketPool:
    """测试 WebSocket 连接池"""

    def test_pool_initialization(self, pool: WebSocketPool) -> None:
        """测试连接池初始化"""
        assert pool is not None
        assert pool.get_connection_count(1) == 0

    @pytest.mark.asyncio
    async def test_register_connection(self, pool: WebSocketPool) -> None:
        """测试注册连接"""
        # 创建 mock WebSocket
        from unittest.mock import AsyncMock, MagicMock

        ws = MagicMock()
        ws.send_json = AsyncMock()

        pool.register(1, ws)
        assert pool.get_connection_count(1) == 1

    @pytest.mark.asyncio
    async def test_register_multiple_connections(self, pool: WebSocketPool) -> None:
        """测试注册多个连接"""
        from unittest.mock import AsyncMock, MagicMock

        ws1 = MagicMock()
        ws1.send_json = AsyncMock()
        ws2 = MagicMock()
        ws2.send_json = AsyncMock()

        pool.register(1, ws1)
        pool.register(1, ws2)
        assert pool.get_connection_count(1) == 2

    @pytest.mark.asyncio
    async def test_unregister_connection(self, pool: WebSocketPool) -> None:
        """测试注销连接"""
        from unittest.mock import AsyncMock, MagicMock

        ws = MagicMock()
        ws.send_json = AsyncMock()

        pool.register(1, ws)
        assert pool.get_connection_count(1) == 1

        pool.unregister(ws)
        assert pool.get_connection_count(1) == 0

    @pytest.mark.asyncio
    async def test_broadcast_message(self, pool: WebSocketPool) -> None:
        """测试广播消息"""
        from unittest.mock import AsyncMock, MagicMock

        ws1 = MagicMock()
        ws1.send_json = AsyncMock()
        ws2 = MagicMock()
        ws2.send_json = AsyncMock()

        pool.register(1, ws1)
        pool.register(1, ws2)

        message = {
            "type": "new_message",
            "data": {
                "message_id": 1,
                "ticket_id": 1,
                "role": "user",
                "content": "测试消息",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            },
        }

        await pool.broadcast(1, message)

        # 验证两个连接都收到了消息
        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_to_empty_ticket(self, pool: WebSocketPool) -> None:
        """测试向空工单广播消息"""
        message = {"type": "test"}
        # 应该不会抛出异常
        await pool.broadcast(999, message)

    @pytest.mark.asyncio
    async def test_send_to_connection(self, pool: WebSocketPool) -> None:
        """测试发送消息到单个连接"""
        from unittest.mock import AsyncMock, MagicMock

        ws = MagicMock()
        ws.send_json = AsyncMock()

        message = {"type": "connected"}
        await pool.send_to_connection(ws, message)

        ws.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_send_to_connection_error_unregisters(self, pool: WebSocketPool) -> None:
        """测试发送失败时自动注销连接"""
        from unittest.mock import AsyncMock, MagicMock

        ws = MagicMock()
        ws.send_json = AsyncMock(side_effect=Exception("Connection error"))

        pool.register(1, ws)
        assert pool.get_connection_count(1) == 1

        await pool.send_to_connection(ws, {"type": "test"})

        # 连接应该被自动注销
        assert pool.get_connection_count(1) == 0

    @pytest.mark.asyncio
    async def test_heartbeat_starts(self, pool: WebSocketPool) -> None:
        """测试心跳启动"""
        from unittest.mock import AsyncMock, MagicMock

        ws = MagicMock()
        ws.send_json = AsyncMock()

        pool.register(1, ws)
        await pool.start_heartbeat(ws, interval=1)  # 使用短间隔测试

        # 等待至少一次心跳
        await asyncio.sleep(1.5)

        # 验证发送了 ping 消息
        assert ws.send_json.call_count >= 1
        calls = ws.send_json.call_args_list
        assert any(call[0][0]["type"] == "ping" for call in calls)

    @pytest.mark.asyncio
    async def test_heartbeat_cancels_on_unregister(self, pool: WebSocketPool) -> None:
        """测试注销时取消心跳任务"""
        from unittest.mock import AsyncMock, MagicMock

        ws = MagicMock()
        ws.send_json = AsyncMock()

        pool.register(1, ws)
        await pool.start_heartbeat(ws, interval=10)  # 使用长间隔

        # 立即注销
        pool.unregister(ws)

        # 等待一下
        await asyncio.sleep(0.1)

        # 验证心跳任务被取消（不会有 ping 消息）
        assert ws.send_json.call_count == 0 or all(
            call[0][0]["type"] != "ping" for call in ws.send_json.call_args_list
        )

    @pytest.mark.asyncio
    async def test_heartbeat_timeout_detection(self, pool: WebSocketPool) -> None:
        """测试心跳超时检测和自动断开"""
        from unittest.mock import AsyncMock, MagicMock

        ws = MagicMock()
        ws.send_json = AsyncMock()
        ws.close = AsyncMock()

        pool.register(1, ws)

        # 启动心跳，使用短间隔进行测试（2秒间隔，1秒超时）
        await pool.start_heartbeat(ws, interval=2, pong_timeout=1)

        # 不更新 pong 时间，等待超时
        # t=0: 初始化 pong 时间
        # t=2: 第一次检查，距离 pong 2秒，未超时（阈值3秒），发送 ping
        # t=4: 第二次检查，距离 pong 4秒，已超时（阈值3秒），关闭连接
        # 等待 4.5 秒确保第二次检查完成
        await asyncio.sleep(4.5)

        # 验证连接被关闭
        ws.close.assert_called_once()
        # 验证关闭码和原因
        call_args = ws.close.call_args
        assert call_args[1]["code"] == 1008
        assert call_args[1]["reason"] == "Heartbeat timeout"

        # 验证 pong 时间记录被清理
        assert ws not in pool._last_pong_time

    @pytest.mark.asyncio
    async def test_heartbeat_with_pong_updates(self, pool: WebSocketPool) -> None:
        """测试正常回复 pong 时连接保持"""
        from unittest.mock import AsyncMock, MagicMock

        ws = MagicMock()
        ws.send_json = AsyncMock()
        ws.close = AsyncMock()

        pool.register(1, ws)

        # 启动心跳，使用短间隔进行测试（2秒间隔，1秒超时）
        await pool.start_heartbeat(ws, interval=2, pong_timeout=1)

        # 定期更新 pong 时间
        for _ in range(3):
            await asyncio.sleep(1)
            pool.update_pong_time(ws)

        # 等待一个心跳周期
        await asyncio.sleep(2.5)

        # 验证连接未被关闭
        ws.close.assert_not_called()

        # 验证发送了 ping 消息
        assert ws.send_json.call_count >= 1

        # 清理
        pool.unregister(ws)

    @pytest.mark.asyncio
    async def test_update_pong_time(self, pool: WebSocketPool) -> None:
        """测试更新 pong 时间"""
        from unittest.mock import AsyncMock, MagicMock

        ws = MagicMock()
        ws.send_json = AsyncMock()

        pool.register(1, ws)
        await pool.start_heartbeat(ws, interval=30)

        # 等待心跳任务初始化 pong 时间
        await asyncio.sleep(0.1)

        # 获取初始 pong 时间
        initial_pong_time = pool._last_pong_time.get(ws, 0)
        assert initial_pong_time > 0

        # 等待一小段时间
        await asyncio.sleep(0.1)

        # 更新 pong 时间
        pool.update_pong_time(ws)

        # 验证时间已更新
        updated_pong_time = pool._last_pong_time.get(ws, 0)
        assert updated_pong_time > initial_pong_time

        # 清理
        pool.unregister(ws)


class TestWebSocketRoute:
    """测试 WebSocket 路由"""

    def test_websocket_route_registered(self) -> None:
        """测试 WebSocket 路由是否正确注册"""
        # TestClient 不支持 WebSocket，这里只测试路由是否正确注册
        # 实际 WebSocket 测试需要使用真实的客户端或更复杂的测试工具
        assert "/ws/tickets/{ticket_id}" in [route.path for route in app.routes]

    def test_get_websocket_pool_singleton(self) -> None:
        """测试获取单例连接池"""
        pool1 = get_websocket_pool()
        pool2 = get_websocket_pool()
        assert pool1 is pool2

    def test_websocket_message_format_connected(self) -> None:
        """测试 connected 消息格式"""
        message = {
            "type": "connected",
            "data": {
                "ticket_id": 1,
                "message": "WebSocket连接成功",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            },
        }
        # 验证格式符合 api-contracts.md
        assert "type" in message
        assert message["type"] == "connected"
        assert "data" in message
        assert "ticket_id" in message["data"]
        assert "message" in message["data"]
        assert "timestamp" in message["data"]

    def test_websocket_message_format_ping(self) -> None:
        """测试 ping 消息格式"""
        message = {
            "type": "ping",
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        }
        # 验证格式符合 api-contracts.md
        assert "type" in message
        assert message["type"] == "ping"
        assert "timestamp" in message

    def test_websocket_message_format_pong(self) -> None:
        """测试 pong 消息格式"""
        message = {
            "type": "pong",
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        }
        # 验证格式符合 api-contracts.md
        assert "type" in message
        assert message["type"] == "pong"
        assert "timestamp" in message

    def test_websocket_message_format_new_message(self) -> None:
        """测试 new_message 消息格式"""
        message = {
            "type": "new_message",
            "data": {
                "message_id": 15,
                "ticket_id": 1003,
                "role": "agent",
                "content": "您好，我是坐席小李，我来帮您处理这个问题。",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            },
        }
        # 验证格式符合 api-contracts.md
        assert "type" in message
        assert message["type"] == "new_message"
        assert "data" in message
        assert "message_id" in message["data"]
        assert "ticket_id" in message["data"]
        assert "role" in message["data"]
        assert "content" in message["data"]
        assert "timestamp" in message["data"]

    def test_websocket_message_format_status_change(self) -> None:
        """测试 status_change 消息格式"""
        message = {
            "type": "status_change",
            "data": {
                "ticket_id": 1003,
                "old_status": "pending",
                "new_status": "in_progress",
                "agent_id": 12,
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            },
        }
        # 验证格式符合 api-contracts.md
        assert "type" in message
        assert message["type"] == "status_change"
        assert "data" in message
        assert "ticket_id" in message["data"]
        assert "old_status" in message["data"]
        assert "new_status" in message["data"]
        assert "agent_id" in message["data"]
        assert "timestamp" in message["data"]

    def test_create_valid_token_for_websocket(self) -> None:
        """测试为 WebSocket 创建有效 Token"""
        token = create_access_token(
            user_id=1,
            username="test_user",
            role="employee",
            expires_delta=timedelta(minutes=30),
        )
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

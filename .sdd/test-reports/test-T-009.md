# 测试报告：T-009 B00-3 WebSocket 连接池管理

**测试时间**：2026-05-21 09:48:20 CST
**Tester Agent ID**：tester

## 结果：PASS

## 测试结果总结

本轮独立验证确认：`WS /ws/tickets/{ticket_id}?token=...` 可以建立连接并收到 `connected` 推送；客户端主动发送 `ping` 时服务端会返回 `pong`；服务端心跳会周期性发送 `ping`，客户端正常回复 `pong` 时连接保持正常。

针对本次修复的重点，已验证服务端会为每个连接维护 `_last_pong_time`，当客户端在“心跳间隔 + 超时容忍”内未回复 `pong` 时，会主动以 `code=1008` 断开连接；断开事件随后触发路由层 `finally` 中的 `unregister()`，连接从池中移除，不影响其他工单连接。本任务结论为 **PASS**。

## 心跳超时检测验证结果

### 场景 A：客户端正常回复 `pong`

- 使用 `FastAPI TestClient.websocket_connect()` 建立连接，收到 `connected`
- 服务端心跳推送第 1 次 `ping` 后，客户端回复 `{"type":"pong","timestamp":"..."}`，服务端更新 `_last_pong_time`
- 后续继续收到下一次 `ping`，连接保持正常，未被关闭

### 场景 B：客户端不回复 `pong`

- 建立连接后收到服务端第 1 次 `ping`
- 客户端保持静默不回 `pong`
- 下一轮超时检查命中后，服务端记录 `Heartbeat timeout detected`，并主动关闭连接
- 客户端侧收到 `WebSocketDisconnect(code=1008, reason="Heartbeat timeout")`
- 连接关闭事件传播完成后，连接池计数归零，`_last_pong_time` 记录已清理

### 场景 C：客户端偶尔回复 `pong`

- 第 1 次 `ping` 后回复 `pong`，连接保持正常
- 第 2 次 `ping` 后不再回复
- 到达超时阈值后，服务端同样主动断开该连接，客户端收到 `code=1008`

补充说明：

- 运行态验证中，为缩短验证时间，将心跳参数临时加速为 `interval=2s`、`pong_timeout=1s`，验证逻辑与正式配置 `30s + 10s` 等价
- 代码静态检查确认路由仍以 `start_heartbeat(websocket, interval=30)` 启动正式心跳，`pong_timeout` 默认值为 10 秒

## 验收标准逐条验证

| # | 标准 | 结果 | 说明 |
|---|------|------|------|
| 1 | `WS /ws/tickets/{ticket_id}?token=...` 可建立连接并收到 `connected` 推送 | PASS | 运行态连接 `/ws/tickets/9301?token=...` 成功收到 `connected`；无效 token 连接被拒绝，客户端收到 `WebSocketDisconnect(code=1008, reason="Invalid token")`。 |
| 2 | 心跳 ping/pong 机制可用 | PASS | 运行态验证确认两条链路均正常：客户端发送 `ping` 时服务端返回 `pong`；服务端定时发送 `ping` 时，客户端回复 `pong` 可保持连接；不回复 `pong` 时会在超时后主动断开。 |
| 3 | 断线后连接从池中清理，不影响其他连接 | PASS | 运行态验证中，同一 `ticket_id=9201` 建立 2 个连接、`ticket_id=9202` 建立 1 个连接；广播到 `9201` 时前两者收到 `new_message`，`9202` 连接不受影响。各连接关闭后池计数分别归零。超时断开场景下，`ticket_id=9102/9103` 的池计数在断开事件处理后也归零。 |

## 技术检查结果

| 检查项 | 结果 | 说明 |
|---|---|---|
| Typecheck passes | PASS | 执行 `PYTHONPATH=.. ./.venv/bin/python -m mypy src/api/routes/websocket.py src/core/websocket_pool.py tests/test_websocket.py`，结果为 `Success: no issues found in 3 source files`。 |
| Lint passes | PASS | 执行 `PYTHONPATH=.. ./.venv/bin/python -m ruff check src/api/routes/websocket.py src/core/websocket_pool.py tests/test_websocket.py`，结果为 `All checks passed!`。 |
| 单元测试覆盖连接、断线、广播、超时场景 | PASS | 执行 `PYTHONPATH=.. ./.venv/bin/python -m pytest tests/test_websocket.py -q`，结果为 `21 passed`。新增/现有用例包含 `test_heartbeat_timeout_detection`、`test_heartbeat_with_pong_updates`、`test_update_pong_time`，并保留连接/断线/广播验证。 |
| WebSocket 消息格式符合 `api-contracts.md` | PASS | 运行态收到的 `connected`、`ping`、`pong`，以及广播烟测中的 `new_message` 结构均与 `docs/api-contracts.md` 当前定义一致；`status_change` 在测试文件中按契约字段构造并校验。 |

## 消息格式验证结果

| 消息类型 | 结果 | 说明 |
|---|---|---|
| `connected` | PASS | 结构为 `type + data(ticket_id/message/timestamp)`，与 `docs/api-contracts.md` 当前定义一致。 |
| `ping` | PASS | 结构为 `type + timestamp`，与 `docs/api-contracts.md` 当前定义一致。 |
| `pong` | PASS | 结构为 `type + timestamp`，与 `docs/api-contracts.md` 当前定义一致。 |
| `new_message` | PASS | 广播运行态烟测中按契约字段成功发送并被同 ticket 连接接收。 |
| `status_change` | PASS | 测试文件中按契约字段构造并校验。 |

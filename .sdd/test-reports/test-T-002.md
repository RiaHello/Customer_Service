# 测试报告：T-002 P02 员工端 Mock 实现

**测试时间**：2026-05-20 23:08 CST+0800  
**Tester Agent ID**：tester subagent

## 结果：PASS

> 注：按用户明确要求，本次未验证“问题 5（工单卡片标题与原型不一致）”，示例数据标题不纳入本轮结论。

## 验收标准逐条验证

| # | 标准 | 结果 | 说明 |
|---|------|------|------|
| 1 | 用户在员工端输入问题并点击发送，对话区出现用户消息和带 AI 标识的回复气泡 | PASS | 启动中的前端开发服务 `http://127.0.0.1:5173` 上实测：以 `employee1 / 123456` 登录员工端，在未选中工单时输入“我的电脑无法开机，怎么办？”并点击发送，页面创建新工单；中心对话区立即出现用户消息和 AI 回复气泡，左侧列表同步新增该工单。 |
| 2 | 用户点击转人工后，顶部状态变为等待人工客服，左侧工单状态同步更新 | PASS | 在新建工单上点击“转人工”后，浏览器实测顶部状态已更新为“等待人工客服”，且“转人工”按钮消失；代码复核 `frontend/src/pages/EmployeePage.vue` 可见当前工单状态通过重建 `tickets` 数组同步为 `pending`，本轮已不再出现上一轮顶部状态卡在“AI助手”的问题。 |
| 3 | 用户在左侧点击历史工单，中心区域加载对应对话；已完成工单输入框为禁用只读 | PASS | 实测切换到“已完结”筛选并点击首条历史工单后，中心区域成功加载该工单完整历史消息；顶部状态显示“已完结”，输入框和发送按钮均为禁用，且不再显示“转人工”按钮。 |
| 4 | 用户切换工单列表筛选（全部/进行中/已完结），列表内容随之变化 | PASS | 浏览器实测筛选切换正常：`全部` 可见 7 条工单（含新建工单），`进行中` 可见 4 条工单，`已完结` 可见 3 条工单；不同筛选下列表内容和数量均发生变化。 |
| 5 | Typecheck passes | PASS | 在 `frontend/` 执行 `npm run type-check`，`vue-tsc --build` 通过。 |
| 6 | Lint passes | PASS | 在 `frontend/` 执行 `npm run lint`，ESLint 通过。 |
| 7 | Mock 数据格式与 api-contracts.md 一致 | PASS | 对照 `docs/api-contracts.md` 复核：`frontend/src/types/ticket.ts` 中 `TicketListItem`、`TicketDetail`、`CreateTicketResponse`、`TransferTicketResponse` 的字段与工单列表/详情/创建/转人工契约一致；`frontend/src/mocks/tickets.ts` 的 `mockTicketList` 仅保留契约定义字段。 |
| 8 | Mock WebSocket 消息格式与 api-contracts.md 一致 | PASS | 对照 `docs/api-contracts.md` 的 WebSocket 契约复核 `frontend/src/composables/useWebSocket.ts`：`connected/new_message/status_change/error` 均保持 `{ type, data }` 结构，`pong` 已修正为根级 `timestamp` 字段（`{ type: 'pong', timestamp: '...' }`），与契约示例一致。 |

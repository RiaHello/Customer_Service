# 测试报告：T-010 用户登录功能闭环（B01）

**测试时间**：2026-05-21 10:40 UTC+8  
**Tester Agent ID**：Cursor tester subagent

## 结果：PASS

## 测试结果总结

本轮最终验证通过。`frontend/.env` 中 `VITE_USE_MOCK=false` 已生效，在浏览器实际联调中，登录页发出了真实 `POST http://localhost:8000/api/auth/login` 请求，成功登录后写入的是后端返回的真实 JWT，页头昵称与 `localStorage.user.display_name` 均为后端返回值 `测试员工`，不再是 Mock 数据 `张三`。

本次复测同时确认：错误密码场景会命中真实后端并返回 `401 + code=1001 + message=用户名或密码错误`，刷新后登录态保持，且仍可访问员工端、坐席端、知识库管理页。

## Mock 禁用验证结果（关键）

### 1. 配置检查

| 检查项 | 结果 | 说明 |
|---|---|---|
| `frontend/.env` 中 `VITE_USE_MOCK=false` | PASS | 文件内容已确认：`VITE_USE_MOCK=false`。 |

### 2. 浏览器请求列表 / 日志

基于浏览器自动化（`http://localhost:5173/login`）抓取到的真实请求：

```text
111. [POST] http://localhost:8000/api/auth/login => [200] OK
113. [POST] http://localhost:8000/api/auth/login => [401] Unauthorized
```

成功登录请求详情：

```text
#111 [POST] http://localhost:8000/api/auth/login
status: [200] OK
referer: http://localhost:5173/
access-control-allow-origin: http://localhost:5173
```

后端运行日志也记录到了同一组真实请求：

```text
INFO: 127.0.0.1 - "POST /api/auth/login HTTP/1.1" 200 OK
INFO: 127.0.0.1 - "POST /api/auth/login HTTP/1.1" 401 Unauthorized
```

### 3. localStorage 内容

成功登录后浏览器 `localStorage` 实测：

```text
token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
user={"user_id":1,"username":"employee1","role":"employee","display_name":"测试员工","created_at":"2026-05-21 02:04:41"}
```

验证结论：

- `localStorage.token` 为真实 JWT，且以 `eyJ` 开头
- `localStorage.user.display_name` 为后端返回值 `测试员工`
- 未出现 `mock-token-*`

### 4. 页头显示内容

登录成功后页面跳转到 `/employee`，页头实际显示：

```text
测试员工
```

### 5. 环境说明

- 本轮通过路径为 `http://localhost:5173`，与后端当前 CORS 白名单一致。
- 额外观察：若从 `127.0.0.1:4173` 或其他未加入白名单的 origin 访问，浏览器可能出现 `net::ERR_FAILED`，这属于当前本地联调 origin 配置差异，不是 Mock 残留。

## 验收标准逐条验证

### 用户要求验收标准

| # | 标准 | 结果 | 说明 |
|---|------|------|------|
| 1 | 使用正确用户名密码可登录并返回 Token | PASS | 浏览器实测 `employee1/123456` 命中真实 `POST /api/auth/login`，返回 `200`，`localStorage.token` 为真实 JWT。 |
| 2 | 使用错误用户名或密码无法登录 | PASS | 浏览器实测 `employee1/wrongpassword` 命中真实 `POST /api/auth/login`，返回 `401 + code=1001 + message=用户名或密码错误`，页面不跳转。 |
| 3 | 返回的用户信息包含 `user_id/username/role/display_name` | PASS | 成功登录后 `localStorage.user` 与接口响应均包含 `user_id / username / role / display_name`。 |

### 任务验收标准（来自 `.sdd/tasks.json`）

| # | 标准 | 结果 | 说明 |
|---|------|------|------|
| 1 | 用户在登录页输入测试账号密码并点击登录，页面成功跳转到员工端且顶部显示用户昵称 | PASS | 浏览器实测跳转到 `/employee`，页头显示 `测试员工`。 |
| 2 | 用户刷新浏览器后仍保持登录状态，可访问员工端、坐席端、知识库管理页 | PASS | 刷新后 `token` 与 `user` 仍在 `localStorage`；页面仍停留在登录后状态，并可访问 `/employee`、`/agent`、`/knowledge`。 |
| 3 | 用户输入错误密码时，页面显示用户名或密码错误提示，不会跳转 | PASS | 浏览器实测停留在 `/login`，页面显示 `用户名或密码错误`。 |

## 技术检查结果

| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| 1 | Frontend typecheck | PASS | `frontend`: `npm run type-check` 通过。 |
| 2 | Frontend lint | PASS | `frontend`: `npm run lint` 通过。 |
| 3 | Backend mypy | PASS | `backend`: `PYTHONPATH=.. .venv/bin/python -m mypy . --config-file ../pyproject.toml` 通过。 |
| 4 | Backend ruff | PASS | `backend`: `PYTHONPATH=.. .venv/bin/python -m ruff check . --config ../pyproject.toml` 通过。 |
| 5 | 登录相关单元测试 | PASS | `backend`: `PYTHONPATH=.. .venv/bin/python -m pytest tests/test_login.py -q` 通过（11/11）。 |
| 6 | 响应格式符合 `api-contracts.md` | PASS | 成功响应为 `code=200/message=success/data.token+user`；失败响应为 `401 + code=1001/message=用户名或密码错误/data=null`。 |
| 7 | `VITE_USE_MOCK=false` 时登录请求命中真实后端 | PASS | 浏览器请求列表出现真实 `POST http://localhost:8000/api/auth/login`。 |
| 8 | 页面不展示 `[Mock]` 标识或 Mock 账号提示 | PASS | 登录页与登录后页面均未发现 `[Mock]` 或 Mock 专用提示。 |
| 9 | 浏览器或等价测试能证明请求命中真实后端而非 `frontend/src/mocks/*` | PASS | `requests`、后端日志、JWT token、`display_name=测试员工` 共同证明当前命中真实后端。 |

## 登录测试结果

| 场景 | 结果 | 说明 |
|---|---|---|
| 前端页面：`employee1/123456` | PASS | 登录成功，跳转 `/employee`，页头显示 `测试员工`。 |
| 前端页面：`employee1/wrongpassword` | PASS | 页面停留在 `/login`，显示 `用户名或密码错误`。 |
| 后端 API：`employee1/123456` | PASS | 返回 `200`，响应包含真实 JWT 和用户信息。 |
| 后端 API：`nonexistent/123456` | PASS | `tests/test_login.py` 覆盖，返回 `401 + code=1001`。 |
| 后端 API：`employee1/wrongpassword` | PASS | `tests/test_login.py` 覆盖，返回 `401 + code=1001`。 |

## 前端联调验证结果

- 浏览器实际联调地址：`http://localhost:5173/login`
- 后端接口地址：`http://localhost:8000/api/auth/login`
- 成功登录后浏览器跳转至：`/employee`
- 刷新后保持登录态，页头继续显示：`测试员工`
- 已验证登录后可访问：`/employee`、`/agent`、`/knowledge`

## 如仍有问题，列出详情

本轮针对 T-010 的验收范围内未发现阻塞问题，可判定通过。

# 开发计划

> 设计阶段与开发阶段的衔接文件。所有开发进度以本文件为准。

**项目名称**：智能客服系统  
**当前版本**：MVP  
**开发模式**：多 Agent 自动化开发（Planner → Developer → Tester）  
**文档版本**：V1.0  
**更新日期**：2026-05-20

---

## 一、功能清单总览

| 序号 | 功能名称 | 一句话描述 | 对应页面 | 优先级 | 状态 |
|------|---------|-----------|---------|--------|------|
| F-01-01 | 账号密码登录 | 用户输入账号密码，获取 Token 并跳转主界面 | P01 | MVP | 待开发 |
| F-02-01 | 发起咨询 | 员工输入问题，AI自动回答或转人工 | P02 | MVP | 待开发 |
| F-02-02 | 查看AI回答 | 员工查看AI生成的回答消息 | P02 | MVP | 待开发 |
| F-02-03 | 继续对话 | 员工继续追问，AI根据历史对话回答 | P02 | MVP | 待开发 |
| F-02-04 | 转人工 | 员工点击按钮转人工，工单进入待处理池 | P02 | MVP | 待开发 |
| F-02-05 | 继续历史对话 | 员工从历史工单列表选择工单继续对话 | P02 | MVP | 待开发 |
| F-03-01 | 查看待处理工单池 | 坐席查看所有 pending 状态工单列表 | P03 | MVP | 待开发 |
| F-03-02 | 主动接单 | 坐席点击工单卡片，将工单状态改为 in_progress | P03 | MVP | 待开发 |
| F-03-03 | 查看工单详情 | 坐席查看工单的完整对话历史 | P03 | MVP | 待开发 |
| F-03-04 | 发送消息 | 坐席输入消息回复员工 | P03 | MVP | 待开发 |
| F-03-05 | 结束工单 | 坐席点击"结束工单"按钮，工单状态改为 completed | P03 | MVP | 待开发 |
| F-03-06 | 实时消息同步 | 坐席端和员工端通过 WebSocket 实时同步消息 | P02/P03 | MVP | 待开发 |
| F-03-07 | AI 辅助面板 | 坐席查看意图识别结果和用户画像 | P03 | MVP | 待开发 |
| F-03-08 | 智能回答建议 | 坐席点击按钮，AI生成建议回复 | P03 | MVP | 待开发 |
| F-03-09 | 工单分类标签 | 坐席查看工单的自动分类标签（IT问题、权限问题等） | P03 | MVP | 待开发 |
| F-04-01 | 上传知识库文档 | 管理员上传 .md 文档，触发入库流程 | P04 | MVP | 待开发 |
| F-04-02 | 查看入库状态 | 管理员查看文档入库进度（processing/completed/failed） | P04 | MVP | 待开发 |
| F-04-03 | 查看文档列表 | 管理员查看所有已入库文档 | P04 | MVP | 待开发 |
| F-03-10 | 查看历史工单 | 坐席查看自己处理过的历史工单 | P03 | V1.1 | 待开发 |
| F-04-04 | 删除文档 | 管理员删除知识库文档及其向量数据 | P04 | V1.2 | 待开发 |
| F-04-05 | 查看文档详情 | 管理员查看文档的切片、关键词、QA对 | P04 | V2.0 | 待开发 |

**MVP 功能数量**：18个  
**后续版本功能数量**：3个

---

## 二、数据契约摘要

> 完整数据契约见 PRD.md 第7章；接口契约见 api-contracts.md

### 统一响应格式

**成功**：
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误**：
```json
{
  "code": <错误码>,
  "message": "<错误描述>",
  "data": null
}
```

**分页**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 核心数据表

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `users` | 用户信息 | id, username, password_hash, role |
| `tickets` | 工单主表 | id, user_id, agent_id, status, created_at |
| `messages` | 消息记录 | id, ticket_id, role, content, timestamp |
| `documents` | 知识库文档 | id, title, status, uploaded_at, processed_at |
| `document_chunks` | 文档切片 | id, document_id, content, chunk_index |
| `qa_pairs` | QA对 | id, document_id, chunk_id, question, answer |
| `vectors` | 向量索引 | id, chunk_id, vector_blob, dimension |
| `keywords` | 关键词索引 | id, chunk_id, keyword, weight |
| `user_profiles` | 用户画像 | id, user_id, query_domains, last_updated |

---

## 二点五、外部服务与测试权限清单

> 进入多智能体自动化开发前必须确认。真实 Key 不写入本文档，只记录字段名、用途和配置状态。

| 服务 | 用途 | 配置项字段 | MVP 必需 | Tester 完整联调权限 | 缺失时策略 | 状态 |
|------|------|------------|----------|---------------------|------------|------|
| 阿里云百炼 LLM | 意图识别、Query改写、RAG生成、智能回答 | `BAILIAN_API_KEY`, `BAILIAN_BASE_URL`, `BAILIAN_LLM_MODEL` | **是** | 测试 Key + 可调用额度（至少100次/天） | Mock 降级：关键词规则回退 + 固定回复模板 | **待确认** |
| 阿里云百炼 Embedding | 向量化检索（Query/Chunk） | `BAILIAN_API_KEY`, `BAILIAN_EMBEDDING_MODEL` | **是** | 测试 Key + 可调用额度（至少100次/天） | Mock 降级：仅使用关键词检索 | **待确认** |
| 阿里云百炼 Reranker | RAG 重排优化 | `BAILIAN_API_KEY`, `BAILIAN_RERANKER_MODEL` | **是** | 测试 Key + 可调用额度（至少50次/天） | Mock 降级：跳过重排，直接使用 RRF Top-3 | **待确认** |

**重要说明**：
1. **必须在开发前确认**：阿里云百炼平台的 API Key、Base URL、模型名称（LLM/Embedding/Reranker）
2. **测试权限要求**：Tester 需要有调用权限和足够额度，否则只能标记 Mock/fallback 验收
3. **Mock 降级策略**：如果外部服务不可用，系统应优雅降级（关键词规则 + 固定模板），但标注为 "降级验收"，不得宣称真实联调通过
4. **配置文件位置**：`backend/.env`（环境变量）和 `backend/config/llm_config.yaml`（模型配置）

**用户确认清单**：
- [ ] 已提供百炼平台 API Key
- [ ] 已提供百炼平台 Base URL（如 `https://dashscope.aliyuncs.com/api/v1/`）
- [ ] 已提供 LLM 模型名称（如 `qwen-plus`）
- [ ] 已提供 Embedding 模型名称（如 `text-embedding-v2`）
- [ ] 已提供 Reranker 模型名称（如 `bge-reranker-v2-m3`）
- [ ] 测试账号有足够额度（至少支持100轮对话 + 10篇文档入库）

---

## 三、前端开发清单

| 序号 | 页面名称 | 涉及功能 | Mock 数据来源 | 状态 |
|------|---------|---------|--------------|------|
| P01 | 登录页 | F-01-01 | `frontend/src/mocks/auth.ts` | 待开发 |
| P02 | 员工端 | F-02-01 ~ F-02-05 | `frontend/src/mocks/tickets.ts`, `frontend/src/mocks/messages.ts` | 待开发 |
| P03 | 坐席端 | F-03-01 ~ F-03-10 | `frontend/src/mocks/tickets.ts`, `frontend/src/mocks/messages.ts` | 待开发 |
| P04 | 知识库管理 | F-04-01 ~ F-04-05 | `frontend/src/mocks/knowledge.ts` | 待开发 |

### 前端自动验收标准

- [ ] 所有页面 UI 与原型一致（布局、配色、字体、圆角、间距）
- [ ] 所有页面使用 Mock 数据可正常交互
- [ ] Mock 数据格式与 api-contracts.md 完全一致
- [ ] WebSocket 连接使用 Mock 实现（模拟实时推送）
- [ ] 响应式布局（1440px 设计稿 + 适配 1280px/1920px）
- [ ] 错误处理和 Loading 状态完整
- [ ] **Agent/Tester 自动验收通过**

> 前端 Mock 页面完成后触发用户门禁，由用户验收 UI/UX 效果；用户确认后自动进入后端基础设施开发。  
> 前端 Mock 只用于前端 MVP 和接口契约对齐；后端业务任务完成时，必须把对应前端 service/page 切到 `VITE_USE_MOCK=false` 的真实后端联调路径。

---

## 四、后端开发清单

| 序号 | 功能名称 | 依赖 | 对应接口 | 状态 |
|------|---------|------|---------|------|
| **基础设施** |
| B00 | 基础设施搭建 | 无 | `GET /health` | 待开发 |
| B00-1 | 数据库初始化脚本 | B00 | 无（内部脚本） | 待开发 |
| B00-2 | 百炼客户端封装 | B00 | 无（内部模块） | 待开发 |
| B00-3 | WebSocket 连接池管理 | B00 | `WS /ws/tickets/{ticket_id}` | 待开发 |
| B00-4 | JWT Token 认证中间件 | B00 | 无（内部模块） | 待开发 |
| **认证模块** |
| B01 | 用户登录 | B00-4 | `POST /api/auth/login` | 待开发 |
| **工单模块** |
| B02 | 发起咨询（含AI回答） | B00-2, B01 | `POST /api/tickets` | 待开发 |
| B03 | 获取工单列表 | B01 | `GET /api/tickets` | 待开发 |
| B04 | 获取工单详情 | B01 | `GET /api/tickets/{id}` | 待开发 |
| B05 | 转人工 | B01, B00-3 | `PUT /api/tickets/{id}/transfer` | 待开发 |
| B06 | 获取待处理工单池 | B01 | `GET /api/tickets/pending` | 待开发 |
| B07 | 坐席接单 | B01, B00-3 | `PUT /api/tickets/{id}/pick` | 待开发 |
| B08 | 结束工单 | B01, B00-3 | `PUT /api/tickets/{id}/complete` | 待开发 |
| B09 | 发送消息 | B01, B00-3 | `POST /api/tickets/{id}/messages` | 待开发 |
| B10 | 获取消息历史 | B01 | `GET /api/tickets/{id}/messages` | 待开发 |
| **AI 辅助模块** |
| B11 | 获取AI辅助信息 | B01, B00-2 | `GET /api/tickets/{id}/ai-assist` | 待开发 |
| B12 | 生成建议回复 | B01, B00-2 | `POST /api/tickets/{id}/suggest-reply` | 待开发 |
| **知识库模块** |
| B13 | 上传知识库文档 | B00-2 | `POST /api/knowledge/documents` | 待开发 |
| B14 | 获取文档列表 | B01 | `GET /api/knowledge/documents` | 待开发 |
| B15 | 获取文档详情 | B01 | `GET /api/knowledge/documents/{id}` | 待开发 |

### 后端任务验收规则

**基础设施、数据库初始化、外部 SDK 客户端封装等底层任务**：可以只做后端验收（单元测试 + 集成测试）

**对应前端页面或 service 的业务任务**：必须在任务内完成真实联调验收，包括：
- `VITE_USE_MOCK=false` 时前端调用真实后端 API
- 对应页面核心操作可用
- 页面不得展示该功能相关 `[Mock]` 数据、Mock 账号提示或 Mock-only 文案
- Tester 能证明请求命中真实后端，而不是 `frontend/src/mocks/*`

**涉及外部服务的后端任务**：
- 必须引用「外部服务与测试权限清单」
- 如果必要 Key / 权限缺失，只能标记 Mock/fallback 验收
- 不得宣称真实外部服务联调通过

**最终 E2E / 回归阶段**：只做全系统复查，不承担第一次前后端联调

---

## 五、功能详情（开发时逐个展开）

> 以下详情在开发阶段由 Developer 和 Tester 逐个展开和验收。

### 基础设施任务

#### B00：基础设施搭建

**描述**：FastAPI 项目初始化、目录结构、健康检查接口

**验收标准**：
- [ ] 项目目录结构符合 PRD.md 规范
- [ ] `GET /health` 返回 200 和 `{"status": "healthy"}`
- [ ] 依赖包安装完整（requirements.txt）
- [ ] 可通过 `uvicorn main:app --reload` 启动

---

#### B00-1：数据库初始化脚本

**描述**：SQLite 数据库表结构创建脚本

**验收标准**：
- [ ] 执行脚本后生成所有9张表（users, tickets, messages, documents, document_chunks, qa_pairs, vectors, keywords, user_profiles）
- [ ] 表字段、类型、约束与 PRD.md 第7章一致
- [ ] 初始化测试账号（至少1个员工、1个坐席、1个管理员）

---

#### B00-2：百炼客户端封装

**描述**：封装阿里云百炼平台的 LLM/Embedding/Reranker API 调用

**验收标准**：
- [ ] `BailianClient` 类支持 LLM、Embedding、Reranker 三种调用
- [ ] 读取 `backend/.env` 和 `backend/config/llm_config.yaml` 配置
- [ ] 实现错误重试机制（3次）
- [ ] 实现降级策略（API 失败时返回降级标识）
- [ ] 单元测试覆盖正常调用和降级场景

---

#### B00-3：WebSocket 连接池管理

**描述**：WebSocket 连接管理器，支持工单消息实时推送

**验收标准**：
- [ ] `WebSocketPool` 类支持连接注册、注销、广播
- [ ] 支持按 ticket_id 筛选推送目标
- [ ] 实现心跳检测（ping/pong）
- [ ] 连接异常时自动清理
- [ ] 单元测试覆盖连接、断线、广播场景

---

#### B00-4：JWT Token 认证中间件

**描述**：JWT Token 生成、验证、中间件拦截

**验收标准**：
- [ ] `create_access_token()` 生成 JWT Token
- [ ] `verify_token()` 验证 Token 有效性
- [ ] 认证中间件拦截未授权请求（返回 401）
- [ ] `/api/auth/login` 和 `/health` 不需要认证
- [ ] 单元测试覆盖 Token 生成、验证、过期场景

---

### 认证模块

#### B01：用户登录

**描述**：用户名密码登录，返回 Token

**依赖**：B00-4（JWT Token）

**对应接口**：`POST /api/auth/login`

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 数据库查询用户并验证密码（bcrypt hash）
- [ ] 成功返回 Token 和用户信息
- [ ] 失败返回 401 和错误码 1001
- [ ] 前端切换 `VITE_USE_MOCK=false`，登录功能可用
- [ ] Tester 验证：真实后端登录成功，Token 可用于后续请求

---

### 工单模块

#### B02：发起咨询（含AI回答）

**描述**：员工发起咨询，AI自动回答（完整RAG链路）

**依赖**：B00-2（百炼客户端）、B01（认证）

**对应接口**：`POST /api/tickets`

**核心流程**：
1. 创建工单，状态 = `ai_answering`
2. 保存用户消息
3. 调用 AI 服务智能回答：
   - 步骤1：QA库直接匹配（相似度 ≥ 0.8 直接返回）
   - 步骤2：意图识别（LLM）
   - 步骤3：Query改写（长短期记忆）
   - 步骤4：RAG检索生成（向量召回 + 关键词召回 + RRF混合 + Reranker重排 + LLM生成）
4. 保存AI消息
5. 更新用户画像（领域+1）
6. 返回工单和AI回答

**验收标准**：
- [ ] 后端接口实现完整，完整RAG链路可执行
- [ ] 如果百炼 API Key 可用，真实调用 LLM/Embedding/Reranker
- [ ] 如果百炼 API Key 不可用，降级到关键词规则回退（标注降级验收）
- [ ] 前端切换 `VITE_USE_MOCK=false`，员工端发起咨询可用
- [ ] Tester 验证：真实后端返回AI回答，工单状态正确

---

#### B03：获取工单列表

**描述**：员工查看历史工单列表

**依赖**：B01（认证）

**对应接口**：`GET /api/tickets`

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 支持分页、状态过滤
- [ ] 前端切换 `VITE_USE_MOCK=false`，员工端历史工单列表可用
- [ ] Tester 验证：真实后端返回工单列表

---

#### B04：获取工单详情

**描述**：查看工单完整对话历史

**依赖**：B01（认证）

**对应接口**：`GET /api/tickets/{id}`

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 返回工单信息和完整消息历史
- [ ] 前端切换 `VITE_USE_MOCK=false`，工单详情页可用
- [ ] Tester 验证：真实后端返回工单详情

---

#### B05：转人工

**描述**：员工点击转人工按钮，工单进入待处理池

**依赖**：B01（认证）、B00-3（WebSocket）

**对应接口**：`PUT /api/tickets/{id}/transfer`

**核心流程**：
1. 检查工单状态（只有 `ai_answering` 可转人工）
2. 更新工单状态 = `pending`
3. WebSocket 推送状态变更消息到坐席端

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 工单状态流转正确
- [ ] WebSocket 实时推送到坐席端
- [ ] 前端切换 `VITE_USE_MOCK=false`，员工端转人工可用
- [ ] Tester 验证：真实后端转人工成功，坐席端实时收到新工单

---

#### B06：获取待处理工单池

**描述**：坐席查看所有 pending 状态工单

**依赖**：B01（认证）

**对应接口**：`GET /api/tickets/pending`

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 只返回 pending 状态工单
- [ ] 前端切换 `VITE_USE_MOCK=false`，坐席端工单池可用
- [ ] Tester 验证：真实后端返回待处理工单

---

#### B07：坐席接单

**描述**：坐席点击工单，将工单状态改为 in_progress

**依赖**：B01（认证）、B00-3（WebSocket）

**对应接口**：`PUT /api/tickets/{id}/pick`

**核心流程**：
1. 检查工单状态（只有 `pending` 可接单）
2. 更新工单状态 = `in_progress`，绑定坐席ID
3. WebSocket 推送状态变更消息到员工端

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 工单状态流转正确
- [ ] WebSocket 实时推送到员工端
- [ ] 防止多个坐席同时接单（乐观锁或分布式锁）
- [ ] 前端切换 `VITE_USE_MOCK=false`，坐席端接单可用
- [ ] Tester 验证：真实后端接单成功，员工端实时收到坐席接单通知

---

#### B08：结束工单

**描述**：坐席点击结束工单按钮，工单状态改为 completed

**依赖**：B01（认证）、B00-3（WebSocket）

**对应接口**：`PUT /api/tickets/{id}/complete`

**核心流程**：
1. 检查工单状态（只有 `in_progress` 可结束）
2. 更新工单状态 = `completed`
3. WebSocket 推送状态变更消息到员工端

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 工单状态流转正确
- [ ] WebSocket 实时推送到员工端
- [ ] 前端切换 `VITE_USE_MOCK=false`，坐席端结束工单可用
- [ ] Tester 验证：真实后端结束工单成功，员工端工单变为只读

---

#### B09：发送消息

**描述**：员工/坐席发送消息，实时推送到对方

**依赖**：B01（认证）、B00-3（WebSocket）

**对应接口**：`POST /api/tickets/{id}/messages`

**核心流程**：
1. 保存消息到数据库
2. WebSocket 推送消息到对方（员工 ↔ 坐席）

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 消息保存正确
- [ ] WebSocket 实时推送到对方
- [ ] 前端切换 `VITE_USE_MOCK=false`，消息发送可用
- [ ] Tester 验证：真实后端发送消息成功，对方实时收到

---

#### B10：获取消息历史

**描述**：查看工单完整消息历史

**依赖**：B01（认证）

**对应接口**：`GET /api/tickets/{id}/messages`

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 支持分页
- [ ] 前端切换 `VITE_USE_MOCK=false`，消息历史可用
- [ ] Tester 验证：真实后端返回消息历史

---

### AI 辅助模块

#### B11：获取AI辅助信息

**描述**：坐席查看意图识别结果和用户画像

**依赖**：B01（认证）、B00-2（百炼客户端）

**对应接口**：`GET /api/tickets/{id}/ai-assist`

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 返回意图识别结果（level1, level2, is_ambiguous）
- [ ] 返回用户画像（query_domains）
- [ ] 前端切换 `VITE_USE_MOCK=false`，坐席端AI辅助面板可用
- [ ] Tester 验证：真实后端返回AI辅助信息

---

#### B12：生成建议回复

**描述**：坐席点击按钮，AI生成建议回复

**依赖**：B01（认证）、B00-2（百炼客户端）

**对应接口**：`POST /api/tickets/{id}/suggest-reply`

**核心流程**：
1. 获取工单对话历史
2. 调用百炼 LLM 生成建议回复
3. 返回建议回复内容

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 如果百炼 API Key 可用，真实调用 LLM
- [ ] 如果百炼 API Key 不可用，降级到固定模板（标注降级验收）
- [ ] 前端切换 `VITE_USE_MOCK=false`，坐席端智能回答可用
- [ ] Tester 验证：真实后端生成建议回复

---

### 知识库模块

#### B13：上传知识库文档

**描述**：管理员上传 .md 文档，触发入库流程（切片、向量化、QA提取）

**依赖**：B00-2（百炼客户端）

**对应接口**：`POST /api/knowledge/documents`

**核心流程**：
1. 保存文档记录，状态 = `processing`
2. 文档切片（按 Markdown 标题分段）
3. 并行处理：
   - 向量化（百炼 Embedding API）
   - 关键词提取（jieba + TF-IDF，每个chunk 5个关键词）
   - QA提取（百炼 LLM）
4. 全部完成后，更新状态 = `completed`

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 文档切片逻辑正确
- [ ] 如果百炼 API Key 可用，真实调用 Embedding/LLM
- [ ] 如果百炼 API Key 不可用，降级到仅关键词索引（标注降级验收）
- [ ] 前端切换 `VITE_USE_MOCK=false`，知识库管理页上传可用
- [ ] Tester 验证：真实后端上传文档成功，入库状态正确

---

#### B14：获取文档列表

**描述**：管理员查看所有已入库文档

**依赖**：B01（认证）

**对应接口**：`GET /api/knowledge/documents`

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 支持分页、状态过滤
- [ ] 前端切换 `VITE_USE_MOCK=false`，知识库管理页文档列表可用
- [ ] Tester 验证：真实后端返回文档列表

---

#### B15：获取文档详情

**描述**：管理员查看文档的切片、关键词、QA对

**依赖**：B01（认证）

**对应接口**：`GET /api/knowledge/documents/{id}`

**验收标准**：
- [ ] 后端接口实现完整
- [ ] 返回文档信息和所有切片详情
- [ ] 前端切换 `VITE_USE_MOCK=false`，文档详情页可用
- [ ] Tester 验证：真实后端返回文档详情

---

## 六、开发顺序建议

**阶段1：前端 MVP（Mock，用户先验收 UI/UX）**
1. P01（登录页）→ P02（员工端）→ P03（坐席端）→ P04（知识库管理）
2. 所有页面使用 Mock 数据交互，不调用后端真实 API
3. 验收（用户门禁）：用户打开页面，确认布局、配色、交互与原型一致

**阶段2：后端基础设施（自动连续执行，不触发用户门禁）**
1. B00（基于 pycore 脚手架初始化项目）→ B00-1（数据库初始化）→ B00-4（JWT 认证）→ B00-2（百炼客户端）→ B00-3（WebSocket）
2. 基于 pycore 框架复制脚手架，禁止自己重写 config/server/logger
3. 验收（Agent 自动）：ruff/mypy 通过、单元测试通过、GET /health 返回 200

**阶段3：用户登录功能闭环（B01）**
1. 后端真实登录 API + 前端登录页 Mock 切真实
2. 验收（用户门禁）：用户在登录页输入账号密码，成功跳转到首页，刷新后仍保持登录

**阶段4：知识库模块闭环（B13 → B14 → B15）**
1. B13（上传文档）→ B14（文档列表）→ B15（文档详情）
2. 必须先于咨询功能，否则 AI 没有数据回答
3. 验收（用户门禁）：用户在知识库页上传 .md 文档，完成入库后可在列表看到，状态变为已入库

**阶段5：发起咨询与 AI 回答闭环（B02 → B03 → B04 → B05）**
1. B02（发起咨询 + AI 回答）→ B03（工单列表）→ B04（工单详情）→ B05（转人工）
2. 依赖知识库数据（阶段4已完成入库）
3. 验收（用户门禁）：员工输入 IT 问题，AI 生成相关回答；可查看历史工单；可转人工

**阶段6：坐席模块闭环（B06 → B07 → B09 → B08）**
1. B06（工单池）→ B07（接单）→ B09（发送消息）→ B08（结束工单）
2. 验收（用户门禁）：坐席可在待处理池接单、查看对话历史、回复员工、结束工单

**阶段7：AI 辅助模块闭环（B11 → B12）**
1. B11（AI辅助面板）→ B12（智能回答建议）
2. 验收（用户门禁）：坐席可查看意图识别结果、点击生成智能建议回复

**阶段8：E2E 回归测试**
1. 完整流程：登录 → 员工发起咨询 → AI回答 → 转人工 → 坐席接单 → 坐席回复 → 结束工单
2. 验收（用户门禁）：全流程通过，无阻塞性 Bug

---

## 七、开发规则

1. **禁止跳过 Plan.md 直接开发**
2. **禁止在 Plan.md 之外另建进度文件**
3. **前端自动验收通过后，直接进入后端开发**（不得要求用户人工验收）
4. **后端业务任务必须包含真实联调验收**（对应前端页面切换 `VITE_USE_MOCK=false`）
5. **涉及外部服务的任务，必须引用"外部服务与测试权限清单"**（API Key 缺失时标注降级验收）
6. **最终 E2E / 回归阶段只做全系统复查，不承担第一次前后端联调**

---

**文档版本**：V1.0  
**维护规则**：Developer 完成任务后更新状态；Tester 验收通过后标记"已完成"

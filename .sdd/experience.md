# 项目经验

> 当前项目长期有效的经验。  
> Developer / Tester / Bugfix 在任务完成后维护本文件。

---

## Harness 系统经验摘要

新项目开始时，Developer / Tester / Bugfix 需要同时参考：

- 当前项目经验：`.sdd/experience.md`
- 系统级经验：`<SDD_V6>/memory/harness-experience.md`

---

## 开发经验

### T-001: B00 基础设施搭建

**任务概述**：初始化 FastAPI 项目结构、依赖管理、配置加载与健康检查接口 GET /health。

**技术要点**：
- **Python 版本探测**：项目使用 python3.11（3.11.12），通过自动探测确认可用
- **虚拟环境**：使用 `.venv` 作为项目虚拟环境，与项目代码并列存放
- **依赖管理**：requirements.txt 包含 FastAPI、SQLAlchemy、Pydantic、百炼 SDK 等核心依赖
- **配置加载**：使用 pydantic-settings 的 BaseSettings + SettingsConfigDict 模式，避免使用废弃的 Field(env=...) 语法
- **项目结构**：按照后端分层规范创建 src/{api,models,db,repositories,services,core} 目录结构

**陷阱与避坑**：
1. **Pydantic V2 兼容性**：
   - ❌ 旧写法：`Field(default="value", env="ENV_VAR")` 已废弃
   - ✓ 新写法：`model_config = SettingsConfigDict(env_file=".env")` + 直接声明字段默认值
   - 原因：Pydantic V2 改变了配置加载方式，必须使用 SettingsConfigDict

2. **FastAPI 事件处理器**：
   - ❌ 旧写法：`@app.on_event("startup")` 已废弃
   - ✓ 新写法：使用 `@asynccontextmanager` 定义 lifespan 函数，传入 FastAPI(lifespan=lifespan)
   - 原因：FastAPI 推荐使用 lifespan 事件处理器统一管理启动和关闭逻辑

3. **PYTHONPATH 配置**：
   - pycore 不通过 pip 安装，而是通过 PYTHONPATH=.. 引入
   - 启动命令：`cd backend && PYTHONPATH=.. python3.11 -m uvicorn src.main:app --reload`
   - 测试命令：`cd backend && PYTHONPATH=.. pytest tests/ -v`

4. **目录结构**：
   - 业务文件必须在 `backend/src/` 下，不要直接在 `backend/` 根目录创建业务模块
   - `__init__.py` 文件必须存在于每个包目录中

**验收通过标准**：
- ✓ GET /health 返回 200 状态码
- ✓ 响应数据格式符合 api-contracts.md 定义
- ✓ data.status 字段为 "healthy"
- ✓ 单元测试通过（2 个测试用例）
- ✓ 无 Pydantic 或 FastAPI 废弃警告

**后续任务建议**：
- 下一步可以开始数据库初始化（T-002）
- 需要确认百炼平台 API Key 是否可用（当前已配置但未测试）
- JWT 认证中间件开发前需要先完成数据库初始化

---

（后续任务经验将在开发过程中追加）

---

### T-001: P01 登录页 Mock 实现

**任务概述**：实现登录页 UI（对齐原型 docs/prototypes）、账号密码表单、记住密码、错误提示；通过 frontend/src/mocks/auth.ts 模拟 POST /api/auth/login；初始化 Vue Router、Pinia、全局布局骨架与 UI 设计规范（灰白高级感）。

**技术要点**：
- **项目初始化**：使用 `npm create vue@latest` 脚手架创建 Vue 3 + TypeScript + Router + Pinia 项目
- **环境变量配置**：使用 `.env` 文件，所有前端变量必须以 `VITE_` 前缀，通过 `import.meta.env` 访问
- **Mock 数据集中管理**：所有 Mock 数据存放在 `frontend/src/mocks/` 目录，格式与 `api-contracts.md` 严格对齐
- **Axios 统一封装**：单一 axios 实例配置 baseURL、timeout、请求/响应拦截器，业务接口封装在 `services/` 目录
- **路由守卫**：在 `router/index.ts` 的 `beforeEach` 中统一校验登录状态，未登录跳转登录页
- **Pinia 状态管理**：使用 Composition API 风格的 store，`defineStore` + `ref` + `computed`
- **UI 设计规范**：灰白高级感配色（Primary: #18181B，Background: #FAFAFA，Accent: #52525B），圆角 8px，极简风格

**陷阱与避坑**：
1. **环境变量命名**：
   - ❌ 错误：`import.meta.env.API_URL`
   - ✓ 正确：`import.meta.env.VITE_API_URL`（必须 `VITE_` 前缀）
   - 原因：Vite 只会注入以 `VITE_` 开头的环境变量到客户端代码

2. **Axios 拦截器位置**：
   - ❌ 错误：在每个页面组件内单独配置拦截器
   - ✓ 正确：在 `services/api.ts` 统一配置，所有业务接口复用同一实例
   - 原因：避免重复代码，统一错误处理逻辑（如 401 跳转登录）

3. **Mock 数据类型对齐**：
   - ❌ 错误：Mock 函数返回类型与 API 响应类型不一致
   - ✓ 正确：Mock 函数返回 `ApiResponse<LoginResponse>` 类型，失败时 `data: null` 仍需保持类型一致
   - 原因：TypeScript 类型检查要求严格类型匹配，避免运行时错误

4. **路由守卫循环跳转**：
   - ❌ 错误：在守卫中使用 `authStore.isLoggedIn` 判断，但 store 初始化依赖路由
   - ✓ 正确：直接读取 `localStorage.getItem('token')` 判断登录状态
   - 原因：避免循环依赖，路由守卫在 store 初始化之前执行

5. **依赖安装问题**：
   - ❌ 错误：部分依赖安装失败导致 `vue-tsc` 无法运行
   - ✓ 正确：`rm -rf node_modules package-lock.json && npm install` 重新安装
   - 原因：npm 缓存或依赖冲突导致部分模块未正确安装

6. **ESLint 全局变量**：
   - ❌ 错误：`localStorage`、`window`、`setTimeout` 报 `no-undef` 错误
   - ✓ 正确：在 `eslint.config.js` 的 `languageOptions.globals` 中声明浏览器全局变量
   - 原因：ESLint 默认不识别浏览器全局对象，需要显式声明

**验收通过标准**：
- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无错误）
- ✓ Mock 数据格式与 api-contracts.md 一致
- ✓ 响应式布局适配 1440px、1280px、1920px（通过 CSS 媒体查询）
- ✓ 登录页展示账号、密码输入框、记住密码选项和登录按钮
- ✓ 输入 Mock 测试账号可成功登录并跳转到员工端
- ✓ 输入错误密码时显示明确错误提示

**后续任务建议**：
- 下一步实现 T-002 员工端 Mock 实现（对话界面、历史工单列表、Mock WebSocket）
- 需要保持 `VITE_USE_MOCK=true`，所有数据继续使用 Mock
- 注意保持 UI 设计规范的一致性（配色、圆角、字体）

---

### T-001 修复：登录页原型对齐与用户昵称显示

**任务概述**：修复测试报告 test-T-001.md 指出的两个问题：登录页文案与原型不一致，登录成功后顶部显示账号名而非昵称。

**修复内容**：
1. **登录页文案修复**：
   - 将"记住密码"改为"记住我"（符合原型规范）
   - 在"记住我"右侧添加"忘记密码？"链接
   - 调整 `.form-options` 布局为 `justify-content: space-between` 实现左右分布

2. **用户昵称显示修复**：
   - 在 Mock 数据 `mockAccounts` 中为每个用户添加 `display_name` 字段（employee1→张三，agent1→李四，admin→王五）
   - 在 `User` 接口中添加 `display_name?: string` 可选字段
   - 在 `AppHeader.vue` 中优先显示 `display_name`，不存在时降级显示 `username`

**技术要点**：
- 使用 `display_name || username` 实现降级显示，兼容未来后端可能不返回昵称的情况
- TypeScript 类型定义使用可选字段 `display_name?`，避免破坏现有类型兼容性
- "忘记密码"功能暂用 `alert` 占位，待后续版本实现真实逻辑

**陷阱与避坑**：
1. **原型文案对齐**：
   - ❌ 错误：仅凭理解实现功能，忽略原型细节文案
   - ✓ 正确：测试报告指出文案不一致时，必须严格按原型文案修复
   - 原因：产品原型是设计评审通过的标准，细节文案直接影响用户体验

2. **用户展示名字段设计**：
   - ❌ 错误：直接用 `username` 字段展示，导致显示账号名而非昵称
   - ✓ 正确：添加独立的 `display_name` 字段用于展示，保持 `username` 用于登录凭证
   - 原因：账号名（登录凭证）与展示名（用户昵称）是不同的概念，应分开字段存储

3. **降级显示策略**：
   - ❌ 错误：只显示 `display_name`，当字段不存在时页面显示空白
   - ✓ 正确：使用 `display_name || username` 降级策略，确保总能显示用户标识
   - 原因：后端可能存在历史数据或某些用户未设置昵称的情况，需要兼容性处理

4. **布局调整**：
   - ❌ 错误：用 `justify-content: flex-start` 导致"忘记密码？"紧贴"记住我"
   - ✓ 正确：使用 `justify-content: space-between` 实现左右分布
   - 原因：符合常见登录页布局规范，视觉上更清晰

**验收通过标准**：
- ✓ 登录页显示"记住我" + "忘记密码？"，布局左右分布
- ✓ 登录成功后顶部显示用户昵称（如"张三"），不显示账号名（如"employee1"）
- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无错误）
- ✓ 所有原有功能不受影响（登录、记住账号、错误提示等）

**后续任务建议**：
- 真实后端实现时，确保 `POST /api/auth/login` 返回的 `user` 对象包含 `display_name` 字段
- 后续实现真实的"忘记密码"功能时，替换当前的 `alert` 占位逻辑
- 考虑在用户设置页面允许用户修改昵称

---

### T-002: P02 员工端 Mock 实现

**任务概述**：实现员工端布局：左侧历史工单列表（筛选全部/进行中/已完结）、中心对话区（用户/AI/人工气泡与状态指示）、底部输入框与转人工按钮；使用 Mock 数据与 Mock WebSocket 模拟实时推送。

**技术要点**：
- **三栏布局设计**：左侧固定宽度工单列表（300px），右侧弹性主对话区，使用 flexbox 实现高度自适应
- **工单筛选逻辑**：全部/进行中（ai_answering + pending + in_progress）/已完结（completed），使用 computed 属性动态过滤
- **对话消息区布局**：用户消息右对齐（气泡背景 #18181b，白色文字），AI/人工消息左对齐（白色气泡，黑色文字），头像图标区分角色
- **状态栏动态显示**：根据工单 status 显示"AI助手"/"等待人工客服"/"人工客服处理中"/"已完结"
- **Mock WebSocket 封装**：`useWebSocket` composable 统一处理真实 WebSocket 和 Mock 模式，支持心跳、消息推送、状态变更
- **输入框状态控制**：已完结工单禁用输入框，AI 回答中工单显示"转人工"按钮，发送中禁用按钮防止重复提交
- **自动滚动到底部**：新消息发送后使用 `nextTick` + `scrollTop` 自动滚动到最新消息

**陷阱与避坑**：
1. **工单列表筛选与当前选中工单的联动**：
   - ❌ 错误：切换筛选后不检查当前工单是否在筛选结果中，导致显示空对话区但左侧无高亮
   - ✓ 正确：使用 `watch` 监听筛选变化，若当前工单不在筛选结果中则清空选择并断开 WebSocket
   - 原因：避免用户困惑，保持 UI 状态一致性

2. **消息发送后自动滚动失效**：
   - ❌ 错误：直接在 `push` 消息后调用 `scrollToBottom()`，DOM 未更新导致滚动位置不对
   - ✓ 正确：使用 `await nextTick()` 等待 DOM 更新完成后再滚动
   - 原因：Vue 的 DOM 更新是异步的，需要等待渲染完成

3. **WebSocket 连接切换时未断开旧连接**：
   - ❌ 错误：切换工单时直接创建新 WebSocket 连接，导致旧连接残留
   - ✓ 正确：在 `selectTicket` 中先调用 `wsConnection.disconnect()` 断开旧连接
   - 原因：避免内存泄漏和重复消息推送

4. **Mock 数据与 API 契约字段对齐**：
   - ❌ 错误：Mock 数据中使用 `title` 字段作为工单标题，但 api-contracts.md 中无此字段
   - ✓ 正确：使用 `last_message` 字段提取前 20 字符作为标题显示，保持与契约一致
   - 原因：Mock 数据必须是 API 契约字段的子集，不得自行添加字段

5. **时间格式化逻辑**：
   - ❌ 错误：直接显示完整时间戳，导致工单列表过于拥挤
   - ✓ 正确：今天显示时:分，昨天显示"昨天"，更早显示月-日，提升可读性
   - 原因：符合常见聊天应用的时间显示习惯

6. **已完结工单的只读状态**：
   - ❌ 错误：只禁用输入框，但"发送"和"转人工"按钮仍可点击
   - ✓ 正确：使用 `isTicketCompleted` computed 属性同时控制输入框 `disabled` 和发送按钮 `disabled`
   - 原因：防止用户对已完结工单误操作

7. **转人工按钮显示逻辑**：
   - ❌ 错误：所有工单都显示转人工按钮，导致已转人工或已完结工单仍显示
   - ✓ 正确：只有 `status === 'ai_answering'` 时显示转人工按钮（使用 `v-if="canTransferToAgent"`）
   - 原因：转人工只能在 AI 回答阶段执行，其他状态不允许转人工

8. **Mock AI 自动回复的实现**：
   - ❌ 错误：在真实后端联调时仍然触发 Mock AI 回复，导致双重消息
   - ✓ 正确：使用 `if (import.meta.env.VITE_USE_MOCK === 'true')` 条件判断，只在 Mock 模式下自动回复
   - 原因：Mock 数据和真实 API 必须严格隔离，避免逻辑混乱

**验收通过标准**：
- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无警告）
- ✓ Mock 数据格式与 api-contracts.md 一致（tickets、messages 响应结构完全对齐）
- ✓ Mock WebSocket 消息格式与 api-contracts.md 一致（new_message、status_change、connected 格式对齐）
- ✓ 工单列表可筛选全部/进行中/已完结，列表内容随之变化
- ✓ 点击工单卡片加载对应对话，已完成工单输入框禁用只读
- ✓ 输入问题并发送，对话区出现用户消息和 AI 回复气泡
- ✓ 点击转人工按钮，顶部状态变为"等待人工客服"，左侧工单状态同步更新

**后续任务建议**：
- 下一步实现 T-003 坐席端 Mock 实现（三栏布局：待处理/处理中/已完成工单池 + 对话详情 + AI 辅助面板）
- 需要保持 `VITE_USE_MOCK=true`，所有数据继续使用 Mock
- 注意坐席端与员工端的工单状态联动（WebSocket 推送状态变更）
- 坐席端需要支持接单、回复、结束工单、智能回答建议等功能

---

### T-001 修复（第2次）：登录页副标题文案与 API 契约对齐

**任务概述**：修复测试报告 test-T-001.md（第2次测试）指出的两个问题：登录页副标题仍与原型不一致，Mock 数据新增字段但 API 契约未同步更新。

**修复内容**：
1. **登录页副标题修复**：
   - 将副标题从"企业 IT 支持平台"改为"请输入您的账号密码登录系统"（与原型 `docs/prototypes/智能客服系统-原型.pen:324` 完全一致）
   - 位置：`frontend/src/pages/LoginPage.vue:6`

2. **API 契约同步更新**：
   - 在 `docs/api-contracts.md` 登录接口的 `user` 对象中添加 `display_name` 字段（可选字段）
   - 添加字段说明：`display_name`（可选）用于界面展示，如后端未返回则前端降级显示 `username`
   - 保持 Mock 数据（`frontend/src/mocks/auth.ts`）和类型定义（`frontend/src/types/auth.ts`）与契约一致

**技术要点**：
- Mock 数据字段必须是 API 契约已定义字段的**子集**，不得擅自添加契约未定义的字段
- 如需新增字段，必须先更新 `docs/api-contracts.md`，再更新 Mock 数据和类型定义
- 页面文案（标题、副标题、按钮文字、提示语）必须与高保真原型文件**完全一致**，不得凭感觉修改

**陷阱与避坑**：
1. **原型文案二次遗漏**：
   - ❌ 错误：第一次修复时只修复了"记住我"和"忘记密码？"，忽略了副标题与原型不一致
   - ✓ 正确：测试报告明确指出副标题文案问题时，必须使用 Grep 工具在原型文件中搜索准确文案，确保完全一致
   - 原因：原型文件是产品评审通过的唯一标准，任何文案偏差都会被 Tester 判定为 FAIL

2. **Mock 数据先行导致契约不一致**：
   - ❌ 错误：为实现功能在 Mock 数据中添加 `display_name` 字段，但未同步更新 `docs/api-contracts.md`
   - ✓ 正确：任何字段变更必须遵循顺序：**契约更新 → Mock 更新 → 类型定义更新**
   - 原因：`docs/api-contracts.md` 是前后端对齐的唯一依据，Mock 数据偏离契约会导致后端实现时字段不匹配

3. **字段说明缺失**：
   - ❌ 错误：只在契约中添加字段示例，未说明字段是否必填、如何降级
   - ✓ 正确：新增字段时必须添加字段说明，明确字段类型、是否可选、前端降级策略
   - 原因：后端开发者需要清晰了解字段定义，避免实现时产生歧义

4. **开发规则第67-70条重申**：
   - `frontend/src/mocks/` 中的数据字段必须是 `docs/api-contracts.md` 中已定义字段的**子集**
   - **禁止**在 Mock 中添加 api-contracts.md 未定义的字段
   - 如需新增字段，必须先更新 `docs/api-contracts.md`，再更新 Mock 数据

**验收通过标准**：
- ✓ 登录页副标题显示"请输入您的账号密码登录系统"（与原型完全一致）
- ✓ `docs/api-contracts.md` 登录接口 `user` 对象包含 `display_name` 字段定义及说明
- ✓ Mock 数据字段与 API 契约完全一致
- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无错误）

**后续任务建议**：
- 后端实现登录接口时，确保返回的 `user` 对象包含 `display_name` 字段（可选）
- 前端任务开始前，必须先读取高保真原型文件，使用 Grep 搜索关键文案，避免遗漏细节
- 任何 API 字段变更必须遵循"契约优先"原则，先更新文档再更新代码

---

### T-002 修复: 员工端 Mock 实现问题1-4修复

**任务概述**：根据测试报告 test-T-002.md，针对性修复4个问题：无法发起首条咨询、转人工流程不可达、Mock 数据字段与契约不一致、WebSocket 消息类型未契约化。

**修复内容**：

1. **问题1 - 无法发起首条咨询**：
   - 移除 `<div v-if="currentTicketId" class="chat-area">` 的 v-if 限制，改为内部占位符 `v-if="!currentTicketId"`
   - 移除 `handleSendMessage()` 中的 `!currentTicketId.value` 返回判断，允许在未选中工单时创建新工单
   - 新建工单成功后自动滚动到底部，并建立 WebSocket 连接

2. **问题2 - 转人工流程不可达**：
   - 在 Mock 数据 `mockTicketList` 中添加 `id: 1000` 的 `ai_answering` 工单
   - 补齐 `mockTicketDetails[1000]` 的详情数据
   - 确保"转人工"按钮在 `ai_answering` 状态下可点击

3. **问题3 - Mock 数据格式与 API 契约不一致**：
   - 拆分 `Ticket` 类型：创建 `TicketListItem` 接口（只包含 `GET /api/tickets` 定义的6个字段）
   - 重定义 `TicketDetail` 接口（不包含 `last_message` 和 `message_count`，只包含详情特有字段）
   - 将 Mock 列表数据 `mockTickets` 改名为 `mockTicketList`，类型为 `TicketListItem[]`
   - 移除 `mockTicketDetails` 中的 `last_message` 和 `message_count` 字段

4. **问题4 - Mock WebSocket 消息格式未按契约定义**：
   - 为所有 WebSocket 消息类型定义明确的 TypeScript 接口：`NewMessageData`, `StatusChangeData`, `ConnectedData`, `ErrorData`, `PongData`
   - 使用联合类型 `WebSocketMessage` 替代 `data: any`
   - 定义客户端心跳包类型 `PingMessage`
   - 在 Mock 心跳中补齐 `pong` 消息推送逻辑

**技术要点**：

- **类型拆分原则**：列表接口和详情接口的字段清单不同，必须分开建模；Mock 数据只能是对应接口契约字段的子集
- **WebSocket 类型安全**：使用联合类型 + 类型守卫确保消息格式严格符合契约，避免 `any` 类型导致运行时错误
- **首条咨询体验优化**：未选中工单时也展示输入区，降低用户操作门槛

**陷阱与避坑**：

1. **列表 Mock 字段溢出**：
   - ❌ 错误：Mock 列表数据包含 `user_id`、`agent_id`、`wait_time_seconds` 等详情字段
   - ✓ 正确：列表 Mock 只包含 `api-contracts.md` 中 `GET /api/tickets` 定义的 `id, status, last_message, created_at, updated_at, message_count`
   - 原因：前端 Mock 必须与后端契约完全对齐，否则后端实现时会产生字段不匹配

2. **TicketDetail 不应包含列表字段**：
   - ❌ 错误：`TicketDetail extends Ticket`，导致详情类型包含 `last_message` 和 `message_count`
   - ✓ 正确：`TicketDetail` 独立定义，只包含 `api-contracts.md` 中 `GET /api/tickets/{id}` 定义的字段
   - 原因：详情接口的响应结构与列表接口不同，不应继承列表类型

3. **WebSocket 消息类型 any 的风险**：
   - ❌ 错误：`data: any` 允许任意结构进入页面逻辑，无法在编译期发现字段错误
   - ✓ 正确：为每种消息类型定义明确的 `data` 接口，使用联合类型 `WebSocketMessage`
   - 原因：TypeScript 类型检查能在编译期发现字段访问错误，避免运行时 crash

4. **首条咨询创建后未自动滚动**：
   - ❌ 错误：创建工单成功后未调用 `scrollToBottom()`
   - ✓ 正确：创建成功后 `await nextTick()` 再 `scrollToBottom()`
   - 原因：DOM 更新是异步的，需要等待渲染完成后再滚动

**验收通过标准**：

- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无错误）
- ✓ 未选中工单时可输入问题并发送，创建新 `ai_answering` 工单
- ✓ 初始 Mock 数据包含 `ai_answering` 工单，"转人工"按钮可点击
- ✓ Mock 列表数据只包含契约定义的6个字段
- ✓ WebSocket 消息类型全部契约化定义，不使用 `any` 类型

**后续任务建议**：

- 下一步实现 T-003 坐席端 Mock 实现（三栏布局 + AI 辅助面板）
- 前端所有 Mock 数据必须严格遵循"字段子集"原则，不得擅自添加契约未定义的字段
- WebSocket 消息类型定义可复用到坐席端实现中

**系统级经验标注**：

- [SYSTEM] 建议回传系统级经验：Mock 列表字段与 api-contracts.md 不一致，且 WebSocket 消息类型使用 `any` 导致契约验证失效。How to apply: 前端任务开始前，先从 api-contracts.md 提取列表/详情字段清单，分别建模；WebSocket 消息必须逐类型定义明确接口，禁止使用 `any`。

---

### T-002 修复（第2次）：转人工状态同步与 WebSocket pong 消息格式对齐

**任务概述**：根据测试报告 test-T-002.md（第2次测试），针对性修复2个残留问题：转人工后顶部状态未同步更新、WebSocket pong 消息格式与 API 契约不一致。

**修复内容**：

1. **问题1 - 转人工后顶部状态未同步**：
   - 现象：点击"转人工"后，左侧工单状态已更新为 `pending`，但顶部状态文案仍显示"AI助手"，"转人工"按钮仍可见
   - 根因：在 `handleTransferToAgent()` 中直接修改 `tickets.value.find()` 返回的对象属性 `ticket.status = 'pending'`，虽然该对象本身是响应式的，但在某些情况下 Vue 3 的响应式追踪可能不稳定
   - 修复：使用 `tickets.value = tickets.value.map()` 创建新数组，确保响应式更新链路稳定触发
   - 位置：`frontend/src/pages/EmployeePage.vue:357-379`

2. **问题2 - WebSocket pong 消息格式不一致**：
   - 现象：Mock pong 消息格式为 `{ type: 'pong', data: { timestamp } }`，但 `docs/api-contracts.md` 契约定义为 `{ type: 'pong', timestamp }`（根级 timestamp，无 data 嵌套）
   - 根因：其他消息类型（new_message、status_change 等）都有 data 字段，开发时误以为所有 WebSocket 消息都需要 data 字段
   - 修复：将 `WebSocketMessage` 联合类型中的 `pong` 定义从 `{ type: 'pong'; data: PongData }` 改为 `{ type: 'pong'; timestamp: string }`，并相应修改 Mock pong 消息构建代码
   - 位置：`frontend/src/composables/useWebSocket.ts:37-48`, `frontend/src/composables/useWebSocket.ts:89-95`

**技术要点**：

- **响应式更新最佳实践**：在 Vue 3 中，虽然响应式对象的属性修改通常能被追踪，但涉及数组元素内部对象属性修改时，使用 `map` / `filter` / `concat` 等返回新数组的方法更加稳定可靠
- **WebSocket 消息格式一致性**：不是所有 WebSocket 消息都遵循相同的结构，心跳消息（ping/pong）通常是简化的根级字段结构，而业务消息（new_message、status_change）才包含 data 嵌套

**陷阱与避坑**：

1. **响应式数组元素属性修改的不稳定性**：
   - ❌ 错误：`const item = arr.find(...); item.prop = newValue`（直接修改查找到的对象属性）
   - ✓ 正确：`arr.value = arr.value.map(item => item.id === targetId ? { ...item, prop: newValue } : item)`（创建新数组）
   - 原因：虽然 Vue 3 的 Proxy 响应式理论上能追踪深层属性变化，但在复杂 computed 依赖链中，使用不可变更新模式更加稳定，避免响应式追踪失效

2. **WebSocket 消息类型契约逐条核对**：
   - ❌ 错误：假设所有 WebSocket 消息都有相同的结构模式（例如都有 data 字段）
   - ✓ 正确：从 `api-contracts.md` 逐个消息类型提取示例，分别建模，不同类型可以有不同的结构
   - 原因：WebSocket 协议的消息格式由业务需求决定，心跳消息通常极简（节省带宽），业务消息才需要复杂的 data 嵌套结构

3. **computed 依赖链的响应式传递**：
   - ❌ 错误：认为只要修改了源数据（tickets.value[i].status），所有 computed（currentTicket、canTransferToAgent、currentStatusText）都会自动更新
   - ✓ 正确：确保源数据的修改方式能被 Vue 响应式系统完整追踪，使用 map/filter 等创建新引用是最保险的方式
   - 原因：Vue 3 的响应式基于 Proxy，但 computed 的依赖收集和触发更新依赖于对象引用变化或属性访问追踪，复杂场景下使用不可变更新模式更可靠

**验收通过标准**：

- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无错误）
- ✓ 转人工后，顶部状态文案立即更新为"等待人工客服"，"转人工"按钮消失
- ✓ WebSocket pong 消息格式符合 `api-contracts.md` 定义（根级 timestamp，无 data 嵌套）

**后续任务建议**：

- 所有数组元素属性修改，优先使用 map/filter 等不可变更新方法，避免直接修改
- WebSocket 消息类型定义时，不要假设所有消息都有相同结构，严格按契约逐类型建模
- 涉及多层 computed 依赖链时，确保源数据修改方式触发稳定的响应式更新

---

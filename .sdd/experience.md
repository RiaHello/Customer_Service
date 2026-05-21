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

### T-006: B00-1 数据库初始化脚本

**任务概述**：创建 SQLite 数据库初始化脚本，生成项目所需的所有核心表（users、tickets、messages、documents、document_chunks、qa_pairs、vectors、keywords、user_profiles），并创建 3 个测试账号（employee1、agent1、admin），密码使用 bcrypt 哈希。

**技术要点**：
- **数据库模型定义**：基于 SQLAlchemy 2.0 的 Mapped 类型注解，使用 DeclarativeBase 作为基类
- **表结构设计**：严格按照 PRD 第7章数据契约定义字段类型、约束、索引和外键关系
- **密码哈希**：使用 bcrypt 库哈希密码，不使用 passlib（避免依赖冲突）
- **初始化脚本**：支持独立运行（`PYTHONPATH=.. python -m src.db.init_db`），幂等性设计（先删除后创建）
- **测试账号**：employee1（员工）、agent1（坐席）、admin（管理员），密码分别为 password123、password123、admin123

**陷阱与避坑**：
1. **SQLAlchemy 保留字段冲突**：
   - ❌ 错误：直接使用 `metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)`
   - ✓ 正确：使用 `msg_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)`
   - 原因：`metadata` 是 SQLAlchemy 的保留字段，必须通过 `mapped_column("metadata", ...)` 显式指定列名

2. **外键约束定义**：
   - ❌ 错误：`user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))`（表名单数）
   - ✓ 正确：`user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))`（表名复数）
   - 原因：外键引用必须使用实际表名（`__tablename__`），不是类名

3. **JSON 字段类型**：
   - ❌ 错误：`keywords: Mapped[list] = mapped_column(JSON)`（缺少 nullable）
   - ✓ 正确：`keywords: Mapped[list] = mapped_column(JSON, nullable=False)`
   - 原因：JSON 字段必须显式声明是否可空，避免运行时错误

4. **datetime 默认值**：
   - ❌ 错误：`created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())`（立即执行）
   - ✓ 正确：`created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)`（传递函数引用）
   - 原因：`default=datetime.now()` 会在模型定义时执行一次，所有记录使用相同时间

5. **bcrypt 密码哈希**：
   - ❌ 错误：使用 `passlib.context.CryptContext` 或 `passlib.hash.bcrypt`
   - ✓ 正确：直接使用 `bcrypt.hashpw()` 和 `bcrypt.gensalt()`
   - 原因：后端开发规范明确要求使用 bcrypt 库，不使用 passlib

6. **索引创建**：
   - ❌ 错误：在类内部使用 `__table_args__ = (Index(...),)`
   - ✓ 正确：在所有模型定义后，使用 `Index("idx_name", Table.column1, Table.column2)` 创建复合索引
   - 原因：避免循环依赖，复合索引应在所有表定义完成后统一创建

7. **PYTHONPATH 设置**：
   - ❌ 错误：`cd backend && python -m src.db.init_db`（无法导入 pycore）
   - ✓ 正确：`cd backend && PYTHONPATH=.. python -m src.db.init_db`
   - 原因：pycore 与 backend 并列存放，需要通过 PYTHONPATH 引入

**验收通过标准**：
- ✓ 数据库初始化脚本成功运行，创建 9 个核心表
- ✓ 测试账号创建成功，密码使用 bcrypt 哈希
- ✓ Python 语法检查通过（`python -m py_compile`）
- ✓ 脚本支持独立运行（`PYTHONPATH=.. python -m src.db.init_db`）
- ✓ 幂等性验证：多次运行脚本结果一致

**后续任务建议**：
- 下一步实现 T-007 JWT Token 认证中间件
- 数据库表结构已确定，可以开始开发 Repository 层（CRUD 操作）
- 测试账号可用于后续 B01 登录功能联调

---

### T-007: B00-4 JWT Token 认证中间件

**任务概述**：实现 JWT Token 认证系统，包括 Token 生成与验证函数、认证中间件、依赖注入函数 (get_current_user) 和单元测试。

**技术要点**：
- **JWT Token 结构**：使用 python-jose 库生成和验证 JWT Token，Token 包含 `sub`(user_id)、`username`、`role` 和 `exp`(过期时间)
- **认证中间件实现**：使用 Starlette 的 BaseHTTPMiddleware，拦截所有 `/api/*` 请求（除白名单路径）
- **白名单路径**：`/health` 和 `/api/auth/login` 免认证可访问
- **Token 注入**：中间件验证 Token 后将用户信息注入 `request.state.user`，供后续路由处理器使用
- **依赖注入**：通过 `get_current_user()` 函数从 `request.state` 提取用户信息
- **错误处理**：无 Token 返回 401 Unauthorized，Token 过期返回 401 Token expired，Token 无效返回 401 Invalid token

**陷阱与避坑**：
1. **中间件返回类型错误**：
   - ❌ 错误：中间件返回 `error_response()` 字典（`return error_response("msg", "CODE", 401)`）
   - ✓ 正确：中间件必须返回 FastAPI Response 对象（`return JSONResponse(status_code=401, content={...})`）
   - 原因：Starlette 中间件的 `dispatch()` 方法必须返回 Response 对象，不能返回字典

2. **JWT 配置从环境变量读取**：
   - ❌ 错误：硬编码 JWT_SECRET_KEY 或使用默认值
   - ✓ 正确：从 `backend/.env` 读取配置，使用 `settings.jwt_secret_key`
   - 原因：生产环境必须使用强密钥，且不能提交到代码仓库

3. **Token 过期时间使用 UTC**：
   - ❌ 错误：使用 `datetime.now()` 或 `timezone.utc`
   - ✓ 正确：使用 `datetime.now(UTC)` (Python 3.11+ 推荐)
   - 原因：JWT Token 的 `exp` 字段必须使用 UTC 时间，避免时区问题

4. **异常链处理**：
   - ❌ 错误：在 except 块中直接 `raise ValueError("Token expired")`
   - ✓ 正确：使用 `raise ValueError("Token expired") from None`
   - 原因：ruff B904 规则要求显式指定异常链（`from err` 或 `from None`），避免异常上下文污染

5. **依赖注入函数的异常类型**：
   - ❌ 错误：`raise error_response("Unauthorized", "UNAUTHORIZED", 401)` (字典不是异常)
   - ✓ 正确：`raise HTTPException(status_code=401, detail="Unauthorized")`
   - 原因：FastAPI 依赖注入函数只能抛出 HTTPException，不能返回字典或其他类型

6. **类型注解完整性**：
   - ❌ 错误：函数返回 `dict` 类型（泛型不完整）
   - ✓ 正确：函数返回 `dict[str, Any]` 类型
   - 原因：mypy 要求 dict 类型指定 key 和 value 的类型

7. **测试覆盖场景**：
   - Token 生成与验证（有效、过期、无效签名、缺少字段）
   - 中间件拦截（无 Token、有效 Token、过期 Token、格式错误的 Authorization 头）
   - 白名单路径（`/health`、`/api/auth/login` 无需认证可访问）

**验收通过标准**：
- ✓ 单元测试通过（12 个测试用例，覆盖 Token 生成、验证、过期、中间件拦截场景）
- ✓ Lint passes（`ruff check` 无错误）
- ✓ Typecheck passes（`mypy` 无错误）
- ✓ 未携带 Token 访问受保护接口返回 401
- ✓ 有效 Token 可访问受保护接口
- ✓ `/api/auth/login` 与 `/health` 无需 Token 即可访问
- ✓ 不硬编码 JWT_SECRET_KEY（从 `.env` 读取）

**后续任务建议**：
- 下一步实现 T-010 用户登录功能闭环（B01），使用 bcrypt 校验密码并返回 JWT Token
- 登录接口需要调用 `create_access_token()` 生成 Token，并在响应中返回 `access_token` 和 `user` 信息
- 前端登录页将 Mock 切换为真实 API（`VITE_USE_MOCK=false`），Token 持久化到 localStorage 并在 Axios 拦截器注入 `Authorization` 头

**系统级经验标注**：
- 无新的跨项目通用问题需要回传系统级经验

---

### T-008: B00-2 百炼客户端封装

**任务概述**：封装阿里云百炼平台客户端，支持 LLM、Embedding、Reranker 调用，实现重试与降级机制，并进行真实联调验证。

**技术要点**：
- **配置加载**：从 `backend/.env` 读取 API Key，从 `backend/config/llm_config.yaml` 读取模型配置
- **dashscope SDK 使用**：使用 `dashscope.Generation.call`、`dashscope.TextEmbedding.call`、`dashscope.TextReRank.call` 调用阿里云百炼 API
- **重试机制**：API 调用失败时重试 3 次，使用指数退避策略（1s → 2s → 4s）
- **降级标识**：最终失败返回 `None`（供上层关键词回退）
- **pycore BasePlugin 集成**：继承 `pycore.plugins.BasePlugin`，实现 `execute` 方法
- **日志记录**：使用 `pycore.core.get_logger()` 记录调用日志和错误日志

**陷阱与避坑**：
1. **配置文件加载问题**：
   - ❌ 错误：使用复杂的 `mock_open` fixture，导致测试挂起
   - ✓ 正确：使用 `StringIO` 模拟文件读取，简化 mock 配置
   - 原因：复杂的 MagicMock 嵌套可能导致 fixture 初始化挂起

2. **API Key 禁止硬编码**：
   - ❌ 错误：在代码中硬编码 `dashscope.api_key = "sk-xxx"`
   - ✓ 正确：从 `settings.bailian_api_key` 读取配置
   - 原因：API Key 是敏感信息，必须从环境变量读取

3. **重试延迟时间控制**：
   - ❌ 错误：重试延迟时间过长（1s、2s、4s），导致测试运行缓慢
   - ✓ 正确：测试中使用较短的延迟时间（0.1s、0.2s、0.4s），生产环境使用标准延迟
   - 原因：单元测试需要快速执行，重试延迟应该在测试配置中减小

4. **返回类型明确性**：
   - ❌ 错误：`content = output.choices[0].message.content`（类型为 Any）
   - ✓ 正确：`content: str = output.choices[0].message.content`（明确类型为 str）
   - 原因：mypy 要求返回值类型明确，避免 `no-any-return` 错误

5. **降级标识设计**：
   - ❌ 错误：失败时抛出异常，导致上层必须捕获异常
   - ✓ 正确：失败时返回 `None`，上层可以通过判断 `None` 触发降级逻辑
   - 原因：降级是正常业务流程，不应该使用异常机制

6. **导入顺序规范**：
   - ❌ 错误：随意排列导入顺序
   - ✓ 正确：使用 ruff 自动修复导入顺序（标准库 → 第三方库 → 本地模块）
   - 原因：ruff I001 规则要求导入顺序一致，提升代码可读性

7. **测试覆盖场景**：
   - LLM 调用（正常、失败、降级、自定义参数）
   - Embedding 调用（正常、失败、降级、指定维度）
   - Reranker 调用（正常、失败、降级、指定 top_k）
   - 重试机制（3次重试、第二次成功）
   - 配置加载（环境变量、YAML 文件、默认配置）

**验收通过标准**：
- ✓ 单元测试通过（22 个测试用例，覆盖正常调用与降级场景）
- ✓ Lint passes（`ruff check` 无错误）
- ✓ Typecheck passes（`mypy` 无错误）
- ✓ BailianClient 可分别调用 LLM、Embedding、Reranker 并返回有效响应
- ✓ 配置从环境变量与 llm_config.yaml 加载，代码中无 API Key 字面量
- ✓ API 失败时返回可识别的降级标识供上层处理，且有错误日志

**后续任务建议**：
- 下一步实现 T-011 知识库上传与入库功能闭环（B13），使用 BailianClient 调用 Embedding 和 LLM
- 需要实现完整 RAG 链路：文档切片 → 向量化（Embedding）→ 关键词提取（jieba）→ QA 提取（LLM）
- 真实联调时确认 API Key 额度充足，避免因配额不足导致失败

**系统级经验标注**：
- [SYSTEM] 建议回传系统级经验：pytest fixture 中使用复杂 MagicMock 嵌套可能导致测试挂起。How to apply: 使用 `StringIO` 模拟文件读取，简化 mock 配置；测试重试机制时使用较短的延迟时间（0.1s），避免测试运行缓慢。

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

### T-003: P03 坐席端 Mock 实现

**任务概述**：实现坐席端三栏布局：左侧待处理/处理中/已完成工单池、中间对话详情与回复区（查看完整历史+智能回答按钮+结束工单按钮）、右侧 AI 辅助面板（意图识别、用户画像、智能回答建议占位）；使用 Mock 数据与 Mock WebSocket。

**技术要点**：

- **三栏布局设计**：左侧固定 300px 工单列表、中间弹性对话区、右侧固定 320px AI 辅助面板，使用 flexbox 实现高度自适应
- **工单分组筛选**：待处理（pending）、处理中（in_progress）、已完成（completed）三个状态分组，使用 computed 动态过滤
- **自动接单逻辑**：坐席点击待处理工单时，自动调用 pickTicket API 将工单状态从 pending 转为 in_progress
- **AI 辅助面板**：包含意图识别（一级/二级意图）、用户画像（常问领域统计）、智能回答建议（一键采用）三个区域
- **智能回答建议**：点击"智能回答"按钮调用 suggestReply API，生成建议回复并展示在右侧面板，点击"一键采用"可填入输入框
- **结束工单功能**：只有处理中状态的工单才显示"结束工单"按钮，点击后将工单状态从 in_progress 转为 completed

**陷阱与避坑**：

1. **坐席端工单列表与员工端区别**：
   - ❌ 错误：坐席端和员工端使用相同的工单列表 API 参数
   - ✓ 正确：坐席端按状态筛选（pending/in_progress/completed），员工端按用户筛选（当前登录用户的工单）
   - 原因：坐席端需要看到所有待处理的工单池，而员工端只能看到自己的工单历史

2. **自动接单时机**：
   - ❌ 错误：用户点击待处理工单后只加载详情，不自动接单
   - ✓ 正确：检测到工单状态为 pending 时，自动调用 pickTicket API 接单，避免坐席还需要额外点击接单按钮
   - 原因：简化坐席操作流程，点击工单即表示接单意图

3. **AI 辅助数据与工单详情的加载时机**：
   - ❌ 错误：分别加载工单详情和 AI 辅助数据，导致两次加载延迟
   - ✓ 正确：在 selectTicket 中并行加载工单详情和 AI 辅助数据（使用 Promise.all 或分别调用）
   - 原因：两个接口相互独立，可以并行加载提升加载速度

4. **智能回答建议的状态管理**：
   - ❌ 错误：suggestedReply 状态在切换工单时未清空，导致上一个工单的建议残留
   - ✓ 正确：在 watch(currentTab) 和 selectTicket 时清空 suggestedReply 状态
   - 原因：避免显示错误的建议回复，每个工单的建议应该独立

5. **工单状态变更后的列表刷新**：
   - ❌ 错误：接单、结束工单后工单状态变更，但左侧列表未刷新，导致工单仍在原分组
   - ✓ 正确：状态变更后调用 loadTickets() 刷新当前分组的工单列表
   - 原因：保持 UI 状态一致性，避免用户困惑

6. **结束工单按钮的显示条件**：
   - ❌ 错误：所有工单都显示"结束工单"按钮
   - ✓ 正确：只有 `status === 'in_progress'` 时显示"结束工单"按钮（使用 `v-if`）
   - 原因：只有处理中的工单才能结束，待处理和已完成工单不允许结束

7. **AI 辅助面板的空状态处理**：
   - ❌ 错误：未选中工单时右侧面板空白，体验不佳
   - ✓ 正确：未选中工单时显示空状态提示"选择工单后显示 AI 辅助信息"
   - 原因：提供更好的用户体验，告知用户面板功能

8. **Mock 数据的完整性**：
   - ❌ 错误：只在 mockTicketList 中添加 pending 工单，未在 mockTicketDetails 中添加对应详情
   - ✓ 正确：同时在 mockTicketList 和 mockTicketDetails 中添加完整的工单数据
   - 原因：避免点击工单时提示"工单不存在"

**验收通过标准**：

- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无警告）
- ✓ Mock 数据格式与 api-contracts.md 一致（AIAssistInfo、SuggestReply 响应结构对齐）
- ✓ 坐席端左侧可看到待处理、处理中、已完成三个分组及工单卡片（含员工昵称、首条消息、等待时长）
- ✓ 点击待处理工单卡片，中间区域展示完整对话历史，工单自动进入处理中分组
- ✓ 在中间输入回复并发送，对话区出现带人工客服标识的消息
- ✓ 点击智能回答按钮，右侧面板展示建议回复且可一键填入输入框
- ✓ 点击结束工单，该工单移至已完成分组

**后续任务建议**：

- 下一步实现 T-004 知识库管理页 Mock 实现（文档列表、上传 .md 按钮、底部入库状态监控条）
- 需要保持 `VITE_USE_MOCK=true`，所有数据继续使用 Mock
- 坐席端与员工端的 WebSocket 实时同步功能将在后端实现后进行真实联调

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

### T-003 修复: 坐席端 Mock 实现问题1-3修复

**任务概述**：根据测试报告 test-T-003.md，针对性修复3个问题：原型文案与结构未对齐、Mock 数据格式与契约不一致、发送人工回复时出现重复消息。

**修复内容**：

1. **问题1 - 原型文案与结构未对齐（强制）**：
   - 添加用户昵称映射：基于 user_id 映射到真实昵称（张三、李四、赵六等）
   - 修复工单卡片显示：从 `#{{id}} 员工` 改为 `#{{id}} {{昵称}}`
   - 修复会话头部显示：从固定 `员工` 改为动态昵称
   - 修复中间空状态文案：从 `请从左侧选择工单` 改为 `AI 正在处理中...`
   - 修复右侧面板空状态：从 `选择工单后显示 AI 辅助信息` 改为 `请从左侧选择工单`
   - 添加右侧面板标题：`AI 辅助` + sparkles 图标
   - 修复智能回答建议标题：从 `智能回答建议` 改为 `智能建议回复`
   - 修复按钮文案：从 `一键采用` 改为 `采用建议`
   - 添加 `重新生成` 按钮：与 `采用建议` 并列
   - 添加 `已解决` 按钮：与 `结束工单` 并列（绿色背景）
   - 添加 `关联知识` 卡片：展示关联文档（硬件故障排查指南.md）

2. **问题2 - Mock 数据格式与契约不一致**：
   - 为待处理工单定义新类型 `PendingTicketListItem`（包含 `wait_time_seconds` 和 `user_id`）
   - 在 `ticketsService` 中添加 `getPendingTickets` 方法（调用 `GET /api/tickets/pending`）
   - 在 `mocks/tickets.ts` 中添加 `mockPendingTicketList` 数据和 `mockGetPendingTickets` 函数
   - 修改 `AgentPage.vue` 中待处理池的数据加载逻辑：待处理工单使用 `getPendingTickets`，处理中和已完成工单使用 `getTickets`
   - 添加 `formatWaitTime` 函数：将 `wait_time_seconds` 转换为友好格式（秒/分钟/小时）
   - 工单卡片根据类型动态渲染：待处理工单展示 `wait_time_seconds`，其他工单展示 `created_at` 计算的时长

3. **问题3 - 发送人工回复时出现重复消息**：
   - 移除本地乐观更新逻辑（319-327行）
   - 只保留 Mock WebSocket 推送路径：通过 `wsConnection.mockPushMessage` 推送消息
   - Mock 模式下消息通过 WebSocket 回流后唯一渲染到界面

**技术要点**：

- **类型拆分原则**：待处理工单与通用工单列表字段不同，必须分开建模；使用类型守卫 `'last_message' in ticket` 判断类型
- **原型文案严格对齐**：所有文案（标题、按钮、提示语）必须与原型文件完全一致，不得凭感觉修改
- **Mock 字段子集规则**：Mock 数据字段必须是 API 契约已定义字段的子集，不得添加契约未定义的字段

**陷阱与避坑**：

1. **联合类型属性访问**：
   - ❌ 错误：直接访问联合类型中不是所有成员都有的属性（如 `ticket.last_message`）
   - ✓ 正确：使用类型守卫 `'last_message' in ticket` 判断后再访问
   - 原因：TypeScript 联合类型只允许访问所有成员共有的属性，需要类型收窄

2. **原型元素遗漏**：
   - ❌ 错误：只修改文案，忽略原型中的新增元素（如"关联知识"卡片、"重新生成"按钮）
   - ✓ 正确：按原型文件逐项对齐，不遗漏任何卡片、按钮或文案
   - 原因：Tester 会严格按原型验收，任何遗漏都会被判定为 FAIL

3. **Mock 数据契约对齐**：
   - ❌ 错误：待处理工单复用通用工单列表契约，缺少 `wait_time_seconds` 和 `user_id` 字段
   - ✓ 正确：为不同接口分别定义类型和 Mock 数据，严格按 API 契约字段清单建模
   - 原因：坐席端待处理池使用 `GET /api/tickets/pending`，与员工端 `GET /api/tickets` 字段不同

4. **双重消息追加问题**：
   - ❌ 错误：先做本地乐观更新，再通过 Mock WebSocket 推送，导致同一条消息出现两次
   - ✓ 正确：Mock 模式下只保留一种消息追加路径（要么乐观更新，要么 WebSocket 回流）
   - 原因：两种路径同时存在会导致重复渲染，Mock 模式下应该统一通过 WebSocket 推送

**验收通过标准**：

- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无错误）
- ✓ 坐席端工单卡片显示员工昵称（如"#2001 赵六"）
- ✓ 会话头部显示员工昵称
- ✓ 待处理工单卡片展示等待时长（从 `wait_time_seconds` 计算）
- ✓ 右侧面板包含"AI 辅助"标题、"智能建议回复"卡片、"采用建议"+"重新生成"按钮、"关联知识"卡片
- ✓ 中间面板包含"已解决"按钮
- ✓ 发送人工回复时不出现重复消息

**后续任务建议**：

- 下一步实现 T-004 知识库管理页 Mock 实现
- 前端所有 Mock 数据必须严格遵循"字段子集"原则，不得擅自添加契约未定义的字段
- 原型对齐检查应在开发前用 Grep 搜索原型文件关键文案，避免遗漏

---

### T-003 修复（第2次）：处理中/已完成分组昵称显示与 AI 辅助数据完整性

**任务概述**：根据测试报告 test-T-003.md（第2次测试），针对性修复2个残留问题：处理中/已完成分组未显示员工昵称、主路径中 AI 辅助面板无数据。

**修复内容**：

1. **问题1 - 处理中/已完成分组昵称显示**：
   - 现象：待处理分组显示"#2001 赵六"，但处理中/已完成分组显示"#1001 员工"
   - 根因：在 `AgentPage.vue:309-321` 中，加载处理中/已完成工单时强制设置 `user_id: 0`，导致昵称映射失效
   - 修复：改为并行加载工单详情获取真实 `user_id`，使用 `Promise.all` + `getTicketDetail` 批量获取详情数据，保留真实的 `user_id` 字段
   - 位置：`frontend/src/pages/AgentPage.vue:307-330`

2. **问题2 - AI 辅助数据覆盖不完整**：
   - 现象：点击待处理工单 `#2001` 后，右侧 AI 辅助面板显示"请从左侧选择工单"
   - 根因：`mockAIAssistData` 只覆盖工单 1000-1003，不覆盖待处理池中的 2001-2003
   - 修复：为待处理工单 2001-2003 补齐 AI 辅助数据（意图识别、用户画像、关键词建议）和智能回复建议
   - 位置：`frontend/src/mocks/ai-assist.ts:57-98`, `frontend/src/mocks/ai-assist.ts:98-108`

**技术要点**：

- **批量加载详情数据**：使用 `Promise.all` 并行加载多个工单详情，避免串行加载导致的性能问题
- **类型安全处理**：在访问 `detailsResponses[index]` 时添加 `detailResponse &&` 检查，避免 TypeScript 类型错误
- **Mock 数据覆盖完整性**：确保 Mock 数据覆盖所有主路径实际使用的工单，不留空白区域

**陷阱与避坑**：

1. **强制覆盖字段导致信息丢失**：
   - ❌ 错误：为了"简化处理"强制设置 `user_id: 0`，导致昵称映射失效
   - ✓ 正确：保留原始数据中的字段，如果需要补齐字段，通过加载详情数据获取，而不是硬编码默认值
   - 原因：硬编码默认值会丢失原始数据中的有效信息，导致 UI 展示异常

2. **Mock 数据覆盖不完整**：
   - ❌ 错误：只为历史工单（1000-1003）准备 AI 辅助数据，忽略主路径使用的待处理工单（2001-2003）
   - ✓ 正确：分析页面的所有数据流，确保 Mock 数据覆盖所有可能访问的工单 ID
   - 原因：主路径是用户最常走的流程，主路径数据缺失会严重影响测试验收

3. **TypeScript 类型守卫**：
   - ❌ 错误：直接访问 `detailsResponses[index].code`，TypeScript 报错"可能 undefined"
   - ✓ 正确：添加 `detailResponse &&` 前置检查，即使逻辑上不可能为 undefined
   - 原因：TypeScript 类型系统需要显式的空值检查，即使运行时不会出现 undefined

4. **列表与详情接口的字段差异**：
   - ❌ 错误：假设列表接口返回所有字段，直接用于渲染昵称等详情信息
   - ✓ 正确：明确列表接口（`GET /api/tickets`）不包含 `user_id`，需要加载详情接口（`GET /api/tickets/{id}`）获取
   - 原因：列表接口通常只返回摘要字段（id、status、last_message 等），详情字段需要单独加载

**验收通过标准**：

- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无错误）
- ✓ 处理中/已完成分组工单卡片显示员工昵称（如"#1001 张三"）
- ✓ 待处理工单接单后，右侧 AI 辅助面板正常加载意图识别、用户画像和智能回复建议

**后续任务建议**：

- Mock 数据准备时，先枚举页面所有数据流（待处理池 + 处理中池 + 已完成池 + 详情弹窗 + AI 辅助面板），确保每个路径都有对应的数据源
- 列表与详情接口字段不同时，优先使用详情接口获取完整数据，而不是在列表数据上硬编码默认值
- 类型检查错误时，添加显式的空值检查，避免假设"逻辑上不可能为空"

**系统级经验标注**：

- [SYSTEM] 建议回传系统级经验：强制覆盖字段导致信息丢失，Mock 数据覆盖不完整导致主路径缺失数据。How to apply: 修复前枚举页面的所有状态分组与数据流，确保 Mock 数据覆盖所有主路径；不要为了"简化处理"硬编码默认值，应通过加载详情数据获取完整字段。

---

### T-003 修复（第3次）：已完成分组工单昵称显示完整性

**任务概述**：根据测试报告 test-T-003.md（第3次测试），针对性修复最后1个残留问题：已完成分组中工单 #1004 和 #1005 未显示昵称。

**修复内容**：

**问题 - 已完成分组中工单 1004 和 1005 昵称显示为"员工"**：
  - 现象：已完成分组中的 `#1004 员工`、`#1005 员工` 显示通用占位文案，而不是昵称（如"#1004 李四"）
  - 根因：`mockTicketDetails` 中缺少工单 1004 和 1005 的详情数据，导致 `getTicketDetail(1004)` 和 `getTicketDetail(1005)` 返回失败，`user_id` 被设置为 0，昵称映射失败
  - 修复：在 `frontend/src/mocks/tickets.ts` 中为工单 1004 和 1005 补齐完整的详情数据（包括 `user_id`、`agent_id`、`messages`）
  - 工单 1004：分配 `user_id: 2`（对应昵称"李四"），5条消息记录
  - 工单 1005：分配 `user_id: 3`（对应昵称"王五"），8条消息记录
  - 位置：`frontend/src/mocks/tickets.ts:322-403`

**技术要点**：

- **Mock 数据完整性检查**：Mock 列表数据（`mockTicketList`）和详情数据（`mockTicketDetails`）必须一一对应，列表中存在的工单 ID 必须在详情数据中有对应项
- **工单详情与列表数据的关系**：列表接口只返回摘要字段，详情接口返回完整字段；页面加载详情时依赖 `mockTicketDetails`，缺失会导致信息显示异常

**陷阱与避坑**：

1. **Mock 数据的一致性检查**：
   - ❌ 错误：只在 `mockTicketList` 中添加工单，未在 `mockTicketDetails` 中添加对应详情
   - ✓ 正确：列表和详情数据必须一一对应，列表中的每个工单 ID 都应该能在详情中查到
   - 原因：页面加载详情时依赖 `getTicketDetail` 接口，如果详情不存在会导致字段缺失

2. **昵称映射的依赖链**：
   - ❌ 错误：认为工单列表数据中有 `last_message` 就足够显示基本信息了
   - ✓ 正确：昵称显示依赖 `user_id` 字段，而列表接口（`GET /api/tickets`）不包含 `user_id`，必须从详情接口获取
   - 原因：不同接口返回字段不同，需要明确每个字段的来源接口

3. **修复前的完整性检查**：
   - ❌ 错误：只修复主路径测试到的工单，忽略其他分组中的工单
   - ✓ 正确：修复前先遍历所有分组（待处理、处理中、已完成）的工单列表，确保每个工单都有对应的详情数据
   - 原因：测试可能不会覆盖所有工单，开发者应该主动检查数据完整性

4. **Mock 数据的分配策略**：
   - ❌ 错误：所有工单都分配相同的 `user_id`，导致测试时无法区分不同用户
   - ✓ 正确：为不同工单分配不同的 `user_id`，确保昵称映射表（`userDisplayNames`）中的所有用户都被使用
   - 原因：真实场景中不同工单对应不同用户，Mock 数据应该模拟真实场景的多样性

**验收通过标准**：

- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无错误）
- ✓ 已完成分组工单卡片显示员工昵称（如"#1004 李四"、"#1005 王五"）
- ✓ 所有分组（待处理、处理中、已完成）的工单都能正常显示昵称

**后续任务建议**：

- 新增 Mock 数据时，先检查列表和详情数据的对应关系，确保一一对应
- 前端页面开发时，明确每个字段的来源接口（列表 vs 详情），避免假设列表接口返回所有字段
- 修复数据显示问题时，优先检查 Mock 数据完整性，再检查页面逻辑

**系统级经验标注**：

- 本次问题是"Mock 数据覆盖不完整"的延续，已在 T-003 修复（第2次）的系统级经验中记录
- 无需新增系统级经验条目

---

### T-004: P04 知识库管理页 Mock 实现

**任务概述**：实现知识库管理页：文档列表（名称、上传时间、processing/completed 状态）、右上角上传 .md 按钮、底部入库状态监控条（切片/向量化/关键词/QA 四步进度）；使用 Mock 数据与动态进度模拟。

**技术要点**：

- **页面布局设计**：顶部导航栏（复用 AppHeader）+ 页面标题与上传按钮 + 表格容器（flex: 1 自适应高度）+ 底部入库进度条（条件渲染）
- **文件上传处理**：使用 `<input type="file" accept=".md">` 隐藏输入框，通过按钮触发 `click()` 事件；使用 `FormData` 封装文件上传请求
- **Mock 进度模拟**：使用 `setTimeout` 模拟四步入库进度（切片 → 向量化 → 关键词提取 → QA 提取），每步间隔 2 秒
- **进度监控机制**：使用 `setInterval` 轮询 Mock 进度数据，动态更新进度条文案；完成后自动移除进度显示并刷新列表
- **状态文案与配色对齐**：processing/completed/failed 三种状态使用不同颜色（橙色/绿色/红色），文案与原型完全一致
- **表格响应式设计**：表头固定（`position: sticky; top: 0`），表格内容区域可滚动（`overflow: auto`）

**陷阱与避坑**：

1. **TypeScript 类型守卫缺失**：
   - ❌ 错误：直接访问 `processingDocuments.value[0].current_step`，TypeScript 报错"可能 undefined"
   - ✓ 正确：在 computed 中添加 `if (!progress) return ''` 前置检查，确保类型安全
   - 原因：数组可能为空，computed 函数中必须显式检查 undefined

2. **Vue 属性顺序规范**：
   - ❌ 错误：`v-for` 在 `v-else` 之后，或 `:disabled` 在 `@click` 之后
   - ✓ 正确：遵循 vue/attributes-order 规范：指令（v-if/v-else/v-for）→ 绑定（:key/:disabled）→ 事件（@click）
   - 原因：ESLint 强制要求属性顺序一致，提升代码可读性

3. **Mock 数据字段对齐**：
   - ❌ 错误：Mock 列表数据包含 `api-contracts.md` 未定义的字段
   - ✓ 正确：Mock 数据字段必须是 API 契约已定义字段的**子集**，完全对齐 `GET /api/knowledge/documents` 响应结构
   - 原因：前后端联调时，Mock 数据结构必须与真实接口一致，避免字段不匹配

4. **进度监控的内存泄漏防范**：
   - ❌ 错误：`setInterval` 启动后未清理，页面切换或文档完成后仍持续轮询
   - ✓ 正确：进度完成后调用 `clearInterval(interval)`，并在延迟后清理 Mock 进度数据
   - 原因：避免内存泄漏和不必要的性能开销

5. **文件上传后的 input 重置**：
   - ❌ 错误：上传成功后未清空 `input.value`，导致无法重复上传同一文件
   - ✓ 正确：在 `finally` 块中设置 `target.value = ''`，确保每次上传都能触发 `change` 事件
   - 原因：浏览器 `<input type="file">` 的 `change` 事件只在文件选择改变时触发，必须手动重置

6. **入库进度文案的动态构建**：
   - ❌ 错误：直接硬编码"当前任务：XX中..."，不展示已完成步骤
   - ✓ 正确：根据 `progress.steps` 对象动态筛选已完成步骤，拼接"已完成：XX、XX"文案
   - 原因：原型明确要求显示"（已完成：文档切片、向量化）"格式的进度提示

7. **原型文案完全对齐**：
   - ❌ 错误：按钮文案使用"上传"或"上传 .md 文件"，表头文案使用"QA 数量"
   - ✓ 正确：按钮文案"上传文档"、表头文案"QA 条目"，与原型 `docs/prototypes/智能客服系统-原型.pen` 完全一致
   - 原因：Tester 会严格按原型验收文案，任何偏差都会判定为 FAIL

**验收通过标准**：

- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无警告）
- ✓ Mock 数据格式与 api-contracts.md 一致（documents 响应结构对齐）
- ✓ 用户在知识库管理页可看到已上传文档列表，含文档名称、上传时间、处理中/已入库状态
- ✓ 用户点击上传并选择 .md 文件后，列表出现新文档且状态为处理中
- ✓ 页面底部入库状态栏展示切片、向量化、关键词、QA 提取进度，完成后状态变为已入库

**后续任务建议**：

- 下一步实现 T-005 后端基础设施搭建（pycore + 健康检查 + 工具链）
- 前端四页 Mock 完成后进入后端开发阶段，按 Plan.md 阶段2推进
- 知识库上传功能的真实联调（T-011）将在后端 B13 完成后进行

---

### T-004 修复: 知识库页原型对齐与重复导航栏移除

**任务概述**：根据测试报告 test-T-004.md，针对性修复2个问题：高保真原型对齐失败（缺少搜索框、统计卡片、部分表格列）、重复导航栏（KnowledgePage 与 App.vue 均渲染头部）。

**修复内容**：

1. **问题1 - 高保真原型对齐失败**：
   - 按照原型文件 `docs/prototypes/智能客服系统-原型.pen` 补齐页面完整结构
   - 添加搜索框（260px宽，占位符"搜索文档..."，带搜索图标）
   - 添加页面副标题："管理和维护 AI 客服的知识文档"
   - 添加4个统计卡片：总文档数、已索引、处理中、QA 条目（使用 computed 动态计算）
   - 修改表格列：从"文档名称/状态/上传时间/Chunk数/QA条目"改为"文档名称/类型/大小/状态/上传时间/操作"
   - 移除原型中不存在的列："Chunk 数"、"QA 条目"（这些数据已移至统计卡片）
   - 添加表格操作列：查看按钮、删除按钮（带图标）
   - 文档名称列添加文件图标

2. **问题2 - 重复导航栏**：
   - 移除 KnowledgePage.vue 中的 `import AppHeader` 和 `<AppHeader />` 渲染
   - 只保留全局布局（App.vue）中的统一头部
   - 页面布局从 `<AppHeader /> + <div class="kb-main">` 简化为 `<div class="kb-main">`

**技术要点**：

- **原型文件解析**：使用 Grep 工具在大型原型文件（173KB）中搜索关键词（"知识库管理"、"搜索"、"统计卡片"、"表格列"），定位页面结构
- **统计数据计算**：使用 computed 属性动态计算统计卡片数据（总数、已索引、处理中、QA条目总和），而非硬编码
- **布局对齐**：搜索框与上传按钮并列右对齐（使用 flexbox gap: 12px），标题与副标题左对齐
- **表格列宽度对齐**：严格按原型定义列宽（类型90px、大小80px、状态100px、上传时间150px、操作120px）

**陷阱与避坑**：

1. **原型文件过大无法直接读取**：
   - ❌ 错误：直接 Read 整个原型文件，遇到 173KB > 100KB 限制失败
   - ✓ 正确：使用 Grep 工具搜索关键词（"知识库管理"、"搜索"、"类型"、"大小"、"操作"），定位相关结构
   - 原因：原型文件包含多个页面，需要精准定位知识库页面的结构

2. **原型结构逐项对齐**：
   - ❌ 错误：只按任务描述实现最小功能，未按原型文件逐项核对完整可见元素
   - ✓ 正确：从原型文件抽取"页面元素清单"（搜索框、统计卡片、表格列、底部状态区），编码后逐项回对
   - 原因：任务描述通常是页面能力摘要，不足以覆盖高保真原型中的全部结构和文案

3. **重复导航栏的根因分析**：
   - ❌ 错误：只移除 KnowledgePage 的 `<AppHeader />`，未检查其他页面是否也有重复
   - ✓ 正确：检查全局布局（App.vue）是否已统一渲染头部，确认只需移除页面级别的重复导航
   - 原因：全局布局已根据路由条件渲染 AppHeader（非登录页显示），页面内不应再重复渲染

4. **表格列的原型对齐误区**：
   - ❌ 错误：认为 Chunk数/QA条目是表格必要列，因为 Mock 数据中有这些字段
   - ✓ 正确：严格按原型定义表格列，Chunk数/QA条目应在统计卡片中展示，不在表格中
   - 原因：原型是产品评审通过的标准，字段存在不等于必须在表格中展示

5. **统计数据的动态计算**：
   - ❌ 错误：硬编码统计数据（如"24篇"、"21篇"），与实际文档数量不一致
   - ✓ 正确：使用 computed 属性从 documents 数组动态计算（总数、已索引、处理中、QA条目总和）
   - 原因：统计数据应与列表数据保持一致，避免出现"统计24篇，列表只显示3篇"的矛盾

6. **操作按钮的占位实现**：
   - ❌ 错误：操作列留空，未实现查看/删除按钮
   - ✓ 正确：添加查看按钮（眼睛图标）和删除按钮（垃圾桶图标），占位但暂不实现逻辑
   - 原因：原型明确显示操作列有两个按钮，即使功能未实现也应渲染占位按钮

**验收通过标准**：

- ✓ Typecheck passes（`npm run type-check` 无错误）
- ✓ Lint passes（`npm run lint` 无错误）
- ✓ 页面包含搜索框（260px宽，占位符"搜索文档..."）
- ✓ 页面包含4个统计卡片（总文档数、已索引、处理中、QA 条目）
- ✓ 表格列为"文档名称/类型/大小/状态/上传时间/操作"，无"Chunk数"、"QA条目"列
- ✓ 文档名称列带文件图标，操作列带查看/删除按钮
- ✓ 页面无重复导航栏，只显示全局头部

**后续任务建议**：

- 下一步实现 T-005 后端基础设施搭建（pycore + 健康检查 + 工具链）
- 前端所有页面开发前，必须先从原型文件提取完整可见元素清单，避免遗漏
- 统计数据应与列表数据保持一致，优先使用 computed 动态计算

**系统级经验标注**：

- 本次问题与 T-003 系统级经验一致："Developer 只按任务摘要实现了最小功能，没有先按原型逐项核对完整可见元素"
- How to apply: 实现 `frontend/src/pages/*` 前先从 `.pen` 原型抽取"页面元素清单"（头部、搜索、统计卡片、表格列、底部状态区等），编码后逐项回对，再交给 Tester 做浏览器验证

---

### T-006 修复: 数据库模型与 PRD 契约对齐

**任务概述**：根据测试报告 test-T-006.md，修正数据库表字段与 PRD 第 7.1 章数据契约不一致的问题，修复 Lint 问题，创建数据库集成测试，并修复幂等性问题。

**修复内容**：

1. **表字段与 PRD 契约对齐**（最严重）：
   - `users` 表：将 `display_name` 改为 `nickname`，添加 `profile_domains`（JSON），添加 `total_queries`（INTEGER，默认 0）
   - `tickets` 表：将 `agent_id` 改为 `assigned_agent_id`
   - `document_chunks` 表：将 `doc_id` 改为 `document_id`，将 `chunk_text` 改为 `content`
   - `user_profiles` 表：将 `profile_domains` 改为 `query_domains`，移除 `total_queries`（已迁移到 `users` 表）

2. **Lint 修复**：
   - 移除未使用的导入 `Float`
   - 修正导入顺序（按字母排序）
   - 使用 `ruff check --fix` 自动清理空白行尾随空格

3. **数据库集成测试**：
   - 创建 `backend/tests/test_db_init.py`，包含 13 个测试用例
   - 测试内容：9 张表创建成功、3 个测试账号存在、密码 bcrypt 哈希验证、表结构与 PRD 一致、外键存在、默认值正确、幂等性验证
   - 使用 SQLite PRAGMA 语句异步查询表结构，避免 greenlet 错误

4. **幂等性修复**：
   - 移除 `Base.metadata.drop_all()` 调用，改为只在表不存在时创建表
   - 测试账号创建前先检查是否已存在，存在则跳过
   - 第二次运行时显示"⊙ 跳过已存在用户"，不破坏已有数据

**技术要点**：

- **PRD 契约优先原则**：数据库表结构必须严格按照 PRD 第 7.1 章定义，字段名、类型、约束必须完全一致
- **幂等性设计**：使用 `create_all()` 而非 `drop_all() + create_all()`，测试账号使用"存在则跳过"策略
- **异步测试最佳实践**：使用 SQLite PRAGMA 语句（如 `PRAGMA table_info()`, `PRAGMA foreign_key_list()`）异步查询表结构，避免使用同步 `inspect(engine.sync_engine)` 导致 greenlet 错误
- **字段名对齐**：PRD 使用 `nickname`（昵称）而非 `display_name`，使用 `assigned_agent_id`（分配的坐席）而非 `agent_id`，使用 `document_id`（文档ID）而非 `doc_id`

**陷阱与避坑**：

1. **PRD 字段名与习惯命名的差异**：
   - ❌ 错误：使用 `display_name` 作为用户展示名字段（符合常见习惯）
   - ✓ 正确：使用 `nickname` 作为用户展示名字段（符合 PRD 定义）
   - 原因：PRD 是产品评审通过的唯一标准，字段命名必须与 PRD 完全一致

2. **用户画像字段的位置**：
   - ❌ 错误：将 `profile_domains` 和 `total_queries` 放在独立的 `user_profiles` 表中
   - ✓ 正确：将 `profile_domains` 和 `total_queries` 放在 `users` 表中，`user_profiles` 表作为扩展保留
   - 原因：PRD 7.1.1 明确要求 `users` 表包含这两个字段

3. **外键字段的完整性**：
   - ❌ 错误：使用 `agent_id` 作为工单分配的坐席字段
   - ✓ 正确：使用 `assigned_agent_id` 作为工单分配的坐席字段
   - 原因：PRD 7.1.2 明确要求使用 `assigned_agent_id`，更明确表达"已分配的坐席"语义

4. **测试中的 greenlet 错误**：
   - ❌ 错误：在异步测试中使用 `inspect(engine.sync_engine)` 查询表结构
   - ✓ 正确：使用 SQLite PRAGMA 语句（如 `PRAGMA table_info()`）异步查询表结构
   - 原因：SQLAlchemy 的 `inspect()` 会尝试在异步上下文中使用同步连接，导致 greenlet 错误

5. **幂等性实现的误区**：
   - ❌ 错误：每次运行时先 `drop_all()` 再 `create_all()`，确保表结构最新
   - ✓ 正确：只使用 `create_all()`（仅在表不存在时创建），测试账号使用"存在则跳过"
   - 原因：`drop_all()` 会清空已有数据，不适合生产环境和多次运行场景

6. **字段类型与契约的对齐**：
   - ❌ 错误：`document_chunks` 表使用 `chunk_text` 字段存储切片内容
   - ✓ 正确：使用 `content` 字段存储切片内容（与 PRD 一致）
   - 原因：后端实现时必须使用 PRD 定义的字段名，避免前后端联调时字段不匹配

**验收通过标准**：

- ✓ 所有表字段与 PRD 第 7.1 章完全一致
- ✓ Lint passes（`ruff check` 无错误）
- ✓ Typecheck passes（`mypy` 无错误）
- ✓ 数据库集成测试全部通过（13 个测试用例）
- ✓ 幂等性验证：第二次运行时跳过已存在用户，不破坏已有数据

**后续任务建议**：

- 下一步实现 T-007 JWT Token 认证中间件
- 后端所有 ORM 操作必须使用 PRD 定义的字段名（`nickname`, `assigned_agent_id`, `document_id`, `content`）
- 前端联调时确保 API 返回的字段名与 PRD 一致

**系统级经验标注**：

- [SYSTEM] 建议回传系统级经验：数据库基础任务未先做"PRD/Plan 字段对照表"，导致 ORM 命名与文档契约偏离。Why: 数据模型一旦与 PRD / Plan 脱节，后续 API、测试数据、前端联调都会连锁返工。 How to apply: 开始实现任何 ORM / 初始化脚本前，先把 `docs/PRD.md` 第 7 章与 `docs/Plan.md` 的字段逐表列成 checklist，并在提交前用自动化测试验证字段、约束和种子数据。

---

### T-008 修复: 百炼客户端真实 API 响应解析问题

**任务概述**：根据测试报告 test-T-008.md，修复百炼客户端在真实联调中暴露的 API 响应解析错误、日志参数冲突、测试跳过条件和 Mock 数据结构对齐问题。

**修复内容**：

1. **问题1 - LLM 响应解析错误**：
   - 现象：LLM 调用收到 200 响应后仍连续 3 次失败并返回 `None`，异常日志为 `'usage'`
   - 根因：代码访问 `response.output.usage`，但真实 DashScope SDK 的 `usage` 字段位于顶层 `response.usage`
   - 修复：改为读取顶层 `response.usage.input_tokens` 和 `response.usage.output_tokens`
   - 位置：`backend/src/plugins/bailian_client.py:164-165`

2. **问题2 - Embedding 响应解析错误**：
   - 现象：Embedding 调用收到 200 响应后仍连续 3 次失败并返回 `None`，异常日志为 `'dict' object has no attribute 'embeddings'`
   - 根因：真实 SDK 的 `response.output` 是 `dict` 类型，不是对象；需要用 `output["embeddings"]` 访问，不能用 `output.embeddings`
   - 修复：改为从 `response.output["embeddings"]` 读取，并检查列表非空后再返回
   - 位置：`backend/src/plugins/bailian_client.py:221-222`

3. **问题3 - Reranker 文档解析错误**：
   - 现象：Reranker 调用返回排序结果，但 `document` 被序列化成 `"None"`，上层无法获得原始文档文本
   - 根因：代码使用 `hasattr(item.document, "text")` 判断，但真实 SDK 的 document 可能是对象（有 `.text` 属性）或 dict（有 `"text"` 键）
   - 修复：同时兼容对象属性（`doc.text`）和字典键（`doc["text"]`）两种结构
   - 位置：`backend/src/plugins/bailian_client.py:297`

4. **问题4 - 日志参数冲突**：
   - 现象：无效 Key 场景下，`logger.warning(..., message=response.message, ...)` 触发 `Logger.warning() got multiple values for argument 'message'`
   - 根因：`message` 是 `logger.warning()` 的第一个位置参数，不能作为结构化字段名
   - 修复：重命名为 `api_message=response.message`
   - 位置：`backend/src/plugins/bailian_client.py:174`, `backend/src/plugins/bailian_client.py:236`, `backend/src/plugins/bailian_client.py:314`

5. **问题5 - 测试问题**：
   - 现象：真实 API 集成测试被 `@pytest.mark.skipif(True, ...)` 永久跳过，无法防止本次真实联调暴露的 SDK 解析问题
   - 根因：开发时为了快速通过单元测试，直接使用 `skipif(True)` 跳过真实联调测试
   - 修复：改为基于环境变量条件跳过（`os.getenv("SKIP_INTEGRATION_TESTS", "true").lower() == "true"`），默认跳过但可通过设置环境变量开启
   - 同时修复测试中的 Mock 数据结构，使其与真实 SDK 响应一致（Embedding output 改为 dict）
   - 位置：`backend/tests/test_bailian_client.py:376`, `backend/tests/test_bailian_client.py:169-222`

**技术要点**：

- **真实 API 响应结构验证**：第三方 SDK 的响应结构不能假设，必须通过真实联调验证字段路径（如 `usage` 在顶层还是嵌套层、`output` 是对象还是 dict）
- **日志结构化字段命名**：避免使用 Python logging 模块的保留参数名（`message`, `args`, `kwargs`）作为结构化字段名
- **测试跳过条件设计**：集成测试应基于环境变量条件跳过，而非永久跳过，方便本地或 CI 中选择性开启
- **Mock 数据结构对齐**：Mock 数据的结构应与真实 API 响应完全一致，避免单元测试通过但真实联调失败

**陷阱与避坑**：

1. **第三方 SDK 响应结构假设**：
   - ❌ 错误：根据 SDK 文档示例假设 `usage` 在 `output` 下，未验证真实响应结构
   - ✓ 正确：通过真实联调验证响应结构，打印完整 response 对象确认字段路径
   - 原因：SDK 文档可能过时或示例不完整，真实响应结构才是唯一准确来源

2. **dict vs object 访问方式混淆**：
   - ❌ 错误：假设所有 SDK 响应都是对象（可用 `.` 访问），导致遇到 dict 时报 `'dict' object has no attribute 'embeddings'`
   - ✓ 正确：先确认字段是对象还是 dict（通过 `isinstance(output, dict)` 或直接测试），使用对应的访问方式
   - 原因：不同 SDK 的响应风格不同，有的用 Pydantic 对象，有的用原生 dict

3. **日志参数名与 logging 模块冲突**：
   - ❌ 错误：使用 `message=xxx` 作为结构化日志字段，导致与 `logger.warning(message, ...)` 的第一个参数冲突
   - ✓ 正确：使用 `api_message=xxx` 或 `error_message=xxx` 等明确的字段名，避免与 logging 模块保留名冲突
   - 原因：Python logging 模块的 `message` 是第一个位置参数，结构化字段使用该名称会导致参数冲突

4. **永久跳过集成测试的风险**：
   - ❌ 错误：为了快速通过单元测试，直接使用 `@pytest.mark.skipif(True, ...)` 永久跳过集成测试
   - ✓ 正确：使用 `@pytest.mark.skipif(os.getenv("SKIP_INTEGRATION_TESTS", "true").lower() == "true", ...)` 基于环境变量条件跳过
   - 原因：永久跳过的测试无法防止真实联调中的问题，应该在有 API Key 和额度时可选择性开启

5. **Mock 数据结构与真实 SDK 不一致**：
   - ❌ 错误：Mock 数据使用 `MagicMock().output.embeddings` 对象结构，但真实 SDK 返回 `dict` 结构
   - ✓ 正确：Mock 数据结构应与真实 SDK 响应完全一致（如 `output = {"embeddings": [...]}`）
   - 原因：Mock 结构不一致会导致单元测试通过但真实联调失败，无法提前发现问题

6. **空列表检查缺失**：
   - ❌ 错误：只检查 `"embeddings" in output`，但不检查列表是否为空，导致空列表 `[]` 被视为成功
   - ✓ 正确：检查 `"embeddings" in output and output["embeddings"]`，确保列表非空
   - 原因：空列表在布尔上下文中为 `False`，但字典键存在检查会返回 `True`

**验收通过标准**：

- ✓ Lint passes（`ruff check` 无错误）
- ✓ Typecheck passes（`mypy` 无错误）
- ✓ 单元测试通过（22 个测试用例）
- ✓ 真实 API 调用成功：
  - LLM 返回文本内容（非 None）
  - Embedding 返回向量列表（维度 1536）
  - Reranker 返回带完整文档内容的排序结果（非 "None"）

**后续任务建议**：

- 下一步实现 T-011 知识库上传与入库功能闭环（B13），使用修复后的 BailianClient
- 真实联调时确认 API Key 额度充足，避免因配额不足导致失败
- 第三方 SDK 集成时，优先进行真实联调验证响应结构，再编写单元测试

**系统级经验标注**：

- [SYSTEM] 建议回传系统级经验：第三方 SDK 集成时未做真实联调验证响应结构，导致字段路径、类型假设错误；永久跳过集成测试导致无法防止真实联调问题。How to apply: 第三方 SDK 集成时，先做 1 次真实联调烟测验证响应结构（打印完整 response），再编写单元测试；集成测试使用基于环境变量的条件跳过，而非永久跳过；Mock 数据结构应与真实 SDK 响应完全一致（dict vs object、字段路径、嵌套层级）。

---

### T-008 修复（第2次）：Reranker 文档提取问题

**任务概述**：根据测试报告 test-T-008.md（第2次测试），修复 Reranker 调用返回结果中 `document` 字段为 `"None"` 的问题。

**修复内容**：

**问题 - Reranker 返回的 document 字段为 "None"**：
  - 现象：`call_reranker()` 真实返回的结果中 `document` 为 `"None"`，上层无法拿到完整文档内容
  - 根因：代码使用 `item.document` 属性访问，但真实 DashScope SDK 返回的 `item` 对象在属性访问时返回 `None`；必须使用字典访问方式 `dict(item).get("document")` 才能获取到真实结构
  - 真实 SDK 响应结构：`{"index": 0, "relevance_score": 0.56, "document": {"text": "电脑无法开机时..."}}`
  - 修复：改用字典访问方式提取文档内容，兼容嵌套字典结构
  - 位置：`backend/src/plugins/bailian_client.py:287-313`

**技术要点**：

- **DashScope SDK 响应对象的访问方式**：SDK 返回的 `response.output.results` 中的 item 对象需要通过 `dict(item)` 转换为字典后访问，属性访问 `item.document` 可能返回 `None`
- **嵌套字典提取**：真实响应中 `document` 字段是一个包含 `text` 键的字典 `{"text": "..."}`，需要两层提取：先提取 `document` 字典，再提取 `text` 字段
- **Mock 数据结构对齐**：使用继承自 `dict` 的 `MockResult` 类，同时支持字典访问和属性访问，确保单元测试与真实 SDK 行为一致

**陷阱与避坑**：

1. **SDK 对象的属性访问陷阱**：
   - ❌ 错误：假设所有 SDK 响应对象都支持属性访问（如 `item.document.text`）
   - ✓ 正确：优先使用字典访问方式 `dict(item).get("document", {}).get("text", "")`，确保能够访问到真实数据
   - 原因：不同 SDK 的响应对象实现方式不同，有些对象的属性访问返回 `None`，而字典访问才能获取真实数据

2. **属性访问与字典访问的优先级**：
   - ❌ 错误：优先使用 `hasattr(item, "document")` 判断后再用 `item.document` 访问
   - ✓ 正确：优先使用 `dict(item)` 转换为字典，再用字典方法访问，属性访问只作为备用
   - 原因：`hasattr()` 可能返回 `True` 但实际属性值为 `None`，字典访问更可靠

3. **嵌套字典的提取逻辑**：
   - ❌ 错误：假设 `document` 字段是字符串，直接使用 `item_dict.get("document", "")`
   - ✓ 正确：先提取 `document` 字典，检查类型后再提取 `text` 字段
   - 原因：真实 SDK 返回的 `document` 是嵌套字典 `{"text": "..."}`，不是直接的字符串

4. **Mock 数据结构的兼容性**：
   - ❌ 错误：使用 `MagicMock` 的 `__iter__` 方法模拟字典访问，但 `dict()` 转换行为不符合预期
   - ✓ 正确：使用继承自 `dict` 的自定义类，同时在 `__init__` 中设置属性，确保字典访问和属性访问都可用
   - 原因：`dict(mock_object)` 的行为取决于对象的 `__iter__` 方法实现，直接继承 `dict` 更可靠

5. **空值处理**：
   - ❌ 错误：未检查 `document_dict` 是否为 `None`，直接访问 `.get("text")`
   - ✓ 正确：先检查 `document_dict` 是否存在，再检查类型后提取 `text` 字段，最终降级为空字符串
   - 原因：API 可能在某些情况下不返回 `document` 字段，需要兼容性处理

**验收通过标准**：

- ✓ Lint passes（`ruff check` 无错误）
- ✓ Typecheck passes（`mypy` 无错误）
- ✓ 单元测试通过（22 passed, 3 skipped）
- ✓ 真实 API 调用验证通过：Reranker 返回完整文档文本（非 `"None"`）

**后续任务建议**：

- 下一步实现 T-011 知识库上传与入库功能闭环（B13）
- 第三方 SDK 集成时，优先使用字典访问方式处理响应数据，避免属性访问陷阱
- Mock 数据结构应继承真实数据类型（如 `dict`），而非完全使用 `MagicMock`

**系统级经验标注**：

- 本次问题是"第三方 SDK 响应结构假设错误"的延续，与 T-008 修复（第1次）的系统级经验一致
- 补充经验：SDK 对象的属性访问可能返回 `None`，即使 `hasattr()` 返回 `True`；优先使用字典访问方式 `dict(item).get(...)` 提取嵌套数据

---

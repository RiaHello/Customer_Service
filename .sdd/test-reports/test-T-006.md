# 测试报告：T-006 B00-1 数据库初始化脚本

**测试时间**：2026-05-21 01:36:00 CST
**Tester Agent ID**：tester

## 结果：PASS

## 测试结果总结

本轮为修复后的独立复测，结论为 **通过**。我实际使用独立临时库执行了两次初始化脚本，并运行 `ruff check src/db/`、`mypy src/db/`、`pytest tests/test_db_init.py -q` 以及多组 `PRAGMA` / SQL 查询；结果确认 9 张核心表、3 个测试账号、重点字段命名、唯一约束、外键约束与幂等行为均符合本轮 T-006 的验收要求。

## 验收标准逐条验证

| # | 标准 | 结果 | 说明 |
|---|------|------|------|
| 1 | 执行初始化脚本后 SQLite 包含 Plan 要求的全部核心表 | PASS | 实际在独立临时库 `t006_retest.db` 上运行两次 `PYTHONPATH=.. ./.venv/bin/python -m src.db.init_db` 后，库中存在 `users`、`tickets`、`messages`、`documents`、`document_chunks`、`qa_pairs`、`vectors`、`keywords`、`user_profiles` 共 9 张核心表。 |
| 2 | 测试账号可使用文档约定的用户名密码登录（供后续 B01 联调） | PASS | 实际库中存在 `employee1` / `agent1` / `admin` 三个账号，密码哈希均为 `$2b$` 前缀 bcrypt 哈希，并分别通过 `password123`、`password123`、`admin123` 的 `bcrypt.checkpw()` 校验。 |
| 3 | 表字段类型与约束与 PRD 数据契约一致 | PASS | 实际通过 `PRAGMA table_info(...)`、`PRAGMA foreign_key_list(...)`、`PRAGMA index_list(users)` 验证，关键字段命名与本轮 PRD 契约对齐，且 `users.username` 唯一约束、`tickets.user_id` / `tickets.assigned_agent_id` / `messages.ticket_id` / `documents.uploaded_by` 外键均存在。 |

## 技术检查结果

| 检查项 | 结果 | 说明 |
|---|---|---|
| Typecheck passes | PASS | 实际执行 `PYTHONPATH=.. ./.venv/bin/mypy src/db/`，输出 `Success: no issues found in 4 source files`。 |
| Lint passes | PASS | 实际执行 `PYTHONPATH=.. ./.venv/bin/ruff check src/db/`，输出 `All checks passed!`。 |
| 单元测试通过 | PASS | 实际执行 `DATABASE_URL=sqlite+aiosqlite:///./t006_retest.db PYTHONPATH=.. ./.venv/bin/pytest tests/test_db_init.py -q`，13 个数据库相关测试全部通过。 |
| 集成测试通过 | PASS | 上述 `tests/test_db_init.py` 已覆盖初始化脚本执行结果、表结构、外键、默认值、测试账号和幂等性检查，可作为本任务要求的数据库集成验证。 |

## PRD 契约对齐验证详情

### 重点修复项验证

| 检查点 | 结果 | 实际验证结果 |
|---|---|---|
| `users` 使用 `nickname` 而非 `display_name` | PASS | `PRAGMA table_info(users)` 返回字段包含 `nickname`，未见 `display_name`。 |
| `users` 存在 `profile_domains`（JSON） | PASS | `PRAGMA table_info(users)` 返回 `profile_domains`，类型为 `JSON`。 |
| `users` 存在 `total_queries` | PASS | `PRAGMA table_info(users)` 返回 `total_queries`，类型为 `INTEGER`；测试账号默认值为 `0`。 |
| `tickets` 使用 `assigned_agent_id` 而非 `agent_id` | PASS | `PRAGMA table_info(tickets)` 返回 `assigned_agent_id`，未见 `agent_id`。 |
| `document_chunks` 使用 `document_id` 而非 `doc_id` | PASS | `PRAGMA table_info(document_chunks)` 返回 `document_id`，未见 `doc_id`。 |
| `document_chunks` 使用 `content` 而非 `chunk_text` | PASS | `PRAGMA table_info(document_chunks)` 返回 `content`，未见 `chunk_text`。 |
| `user_profiles` 使用 `query_domains` 而非 `profile_domains` | PASS | `PRAGMA table_info(user_profiles)` 返回 `query_domains`，未见 `profile_domains`。 |

### 约束与字段类型验证

| 项目 | 结果 | 说明 |
|---|---|---|
| `users.username` 唯一约束 | PASS | `PRAGMA index_list(users)` 返回唯一索引 `ix_users_username`。 |
| `tickets.user_id` 外键 | PASS | `PRAGMA foreign_key_list(tickets)` 包含 `user_id -> users.id`。 |
| `tickets.assigned_agent_id` 外键 | PASS | `PRAGMA foreign_key_list(tickets)` 包含 `assigned_agent_id -> users.id`。 |
| `messages.ticket_id` 外键 | PASS | `PRAGMA foreign_key_list(messages)` 包含 `ticket_id -> tickets.id`。 |
| `documents.uploaded_by` 外键 | PASS | `PRAGMA foreign_key_list(documents)` 包含 `uploaded_by -> users.id`。 |

## 新增测试验证结果

| 测试文件 | 结果 | 说明 |
|---|---|---|
| `backend/tests/test_db_init.py` | PASS | 实际运行通过，共 13 项测试。 |
| 表结构覆盖 | PASS | 覆盖 9 张核心表、关键字段、外键、唯一约束。 |
| 测试账号覆盖 | PASS | 覆盖 3 个测试账号存在性与 bcrypt 哈希校验。 |
| 幂等性覆盖 | PASS | 覆盖重复初始化后账号数量不变。 |

## 幂等性验证结果

| 检查项 | 结果 | 说明 |
|---|---|---|
| 初始化脚本运行两次 | PASS | 实际对同一临时库执行两次，第二次执行成功。 |
| 不使用 `drop_all()` | PASS | 代码与运行日志均表明脚本只执行 `Base.metadata.create_all`。 |
| 测试账号不重复创建 | PASS | 第二次执行时日志显示 3 个账号均被跳过，`users` 表总数保持为 3。 |

## 测试账号验证结果

| 用户名 | 预期密码 | 角色 | 库内存在 | bcrypt 哈希 | 哈希校验 |
|---|---|---|---|---|---|
| `employee1` | `password123` | `employee` | PASS | PASS | PASS |
| `agent1` | `password123` | `agent` | PASS | PASS | PASS |
| `admin` | `admin123` | `admin` | PASS | PASS | PASS |

## 备注

- `pytest` 运行过程中存在来自 `pycore` 的 Pydantic v2 deprecation warning，但不影响本任务 T-006 的数据库初始化验收结果。
- `docs/Plan.md` 的“数据契约摘要”仍保留部分旧字段命名摘要；本次代码与测试已按 `docs/PRD.md` 第 7 章完成对齐，不影响 T-006 通过判定。

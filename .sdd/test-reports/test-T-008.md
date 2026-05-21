# 测试报告：T-008 B00-2 百炼客户端封装

**测试时间**：2026-05-21 09:26:11 CST
**Tester Agent ID**：tester

## 结果：PASS

## 测试结果总结

本轮在**默认环境（保留 `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY`）**下直接实例化 `BailianClient` 做真实百炼联调，LLM、Embedding、Reranker 三类调用全部成功，说明本次新增的 `trust_env=False` 已有效阻断代理环境变量继承。

同时，`ruff`、`mypy`、单元测试均通过；使用无效 API Key 复测时，客户端会记录清晰错误日志，按 3 次重试后返回 `None`，满足降级标识要求。

## 验收标准逐条验证

| # | 标准 | 结果 | 说明 |
|---|------|------|------|
| 1 | `BailianClient` 可分别调用 LLM、Embedding、Reranker 并返回有效响应 | PASS | 在默认代理环境下真实联调，`call_llm()` 返回有效文本，`call_embedding()` 返回 1 条 1536 维向量，`call_reranker()` 返回 2 条有效排序结果。 |
| 2 | 配置从环境变量与 `llm_config.yaml` 加载，代码中无 API Key 字面量 | PASS | `backend/src/core/config.py` 通过 `_EnvLoader` 从 `backend/.env` 加载环境变量，`backend/src/plugins/bailian_client.py` 从 `backend/config/llm_config.yaml` 加载模型与重试参数；`backend/src` 范围未发现真实 API Key 字面量。 |
| 3 | API 失败时返回可识别的降级标识供上层处理，且有错误日志 | PASS | 将运行中客户端的 `api_key` 改为无效值后，LLM 调用记录 `401` 与 `Invalid API-key provided.` 日志，3 次重试后返回 `None`。 |

## 技术检查结果

| 检查项 | 结果 | 说明 |
|---|---|---|
| Typecheck passes | PASS | 执行 `PYTHONPATH=.. ./.venv/bin/python -m mypy src/plugins tests/test_bailian_client.py`，结果为 `Success: no issues found in 3 source files`。 |
| Lint passes | PASS | 执行 `PYTHONPATH=.. ./.venv/bin/python -m ruff check src/plugins tests/test_bailian_client.py`，结果为 `All checks passed!`。 |
| 单元测试覆盖正常调用与降级场景 | PASS | 执行 `PYTHONPATH=.. ./.venv/bin/python -m pytest tests/test_bailian_client.py -q`，结果为 `22 passed, 3 skipped`。 |
| 必要服务 Key 已按配置文件字段提供且未硬编码 | PASS | 当前运行环境可直接完成真实联调，且 `backend/src` 范围未发现真实 Key 硬编码。 |
| Tester 具备调用百炼完成真实联调的权限 | PASS | 本轮已在默认环境下完成真实百炼联调，并补充验证无效 Key 失败路径。 |
| 外部服务调用失败时有清晰错误处理和日志 | PASS | 无效 Key 场景下有明确 `401` 日志、重试链路和最终 `None` 降级返回。 |

## 默认环境（有代理）真实 API 调用结果

### 真实联调环境

- 调用方式：不清理任何代理环境变量，直接在项目虚拟环境中实例化 `BailianClient`
- 代理变量状态：`HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY` 均存在
- 配置来源：`backend/.env` + `backend/config/llm_config.yaml`

### 关键验证结果

| 能力 | 结果 | 观察 |
|---|---|---|
| LLM | PASS | 返回有效文本：`联调成功` |
| Embedding | PASS | 返回 1 条向量，维度为 `1536` |
| Reranker | PASS | 返回 2 条排序结果，首条结果命中文档“电脑无法开机时，先检查电源线和插座是否正常，再长按电源键10秒后重试。” |

结论：在当前**默认代理环境**下，`BailianClient` 已可直接稳定调用百炼三类能力，不需要手动清除任何代理变量。

## 规范对照结果

| 规范文件 | 结果 | 说明 |
|---|---|---|
| `harness-core/dev-standards/backend-dev.mdc` | PASS | `backend/src/plugins/bailian_client.py` 三处 `httpx.AsyncClient()` 均显式设置 `trust_env=False`，符合“网络客户端不得继承环境变量”的强制要求。 |
| `harness-core/dev-standards/backend-plugin.mdc` | PASS | 未使用 `dashscope` SDK，已采用 `httpx` 直接请求百炼 HTTP API，并手动解析 JSON 响应。 |
| `harness-core/dev-standards/backend-layers.mdc` | PASS | 当前实现位于 `plugins/` 层，未发现明显分层反向依赖。 |

补充规范核对：

- `backend/src/plugins/bailian_client.py` 中 `httpx.AsyncClient()` 出现 3 次，均为 `trust_env=False`
- `backend/src` 范围未发现 `import dashscope` / `from dashscope`

## Lint / Mypy / 测试验证结果

| 命令 | 结果 |
|---|---|
| `PYTHONPATH=.. ./.venv/bin/python -m ruff check src/plugins tests/test_bailian_client.py` | PASS |
| `PYTHONPATH=.. ./.venv/bin/python -m mypy src/plugins tests/test_bailian_client.py` | PASS |
| `PYTHONPATH=.. ./.venv/bin/python -m pytest tests/test_bailian_client.py -q` | PASS（`22 passed, 3 skipped`） |

补充说明：

- `pytest` 中 3 个 `integration` 用例仍默认跳过，本轮真实联调结论来自 Tester 独立执行的真实百炼烟测
- 测试输出包含 `PytestUnknownMarkWarning: Unknown pytest.mark.integration`，不影响本轮验收结论

## 配置验证结果

| 检查项 | 结果 | 说明 |
|---|---|---|
| `backend/config/llm_config.yaml` 存在且格式正确 | PASS | 包含 `llm`、`embedding`、`reranker`、`retry` 四段配置。 |
| `backend/.env` 具备百炼必需字段 | PASS | 运行时成功实例化 `BailianClient` 并完成真实联调，说明环境变量已按字段提供。 |
| 配置加载逻辑 | PASS | `.env` 负责密钥与基础配置，YAML 负责模型与重试参数。 |
| 代码中无真实 API Key 字面量 | PASS | `backend/src` 范围未发现真实 API Key 字面量。 |

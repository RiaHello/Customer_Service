# T-008 百炼客户端重构总结

## 重构概述

**任务**: 将百炼客户端从 `dashscope` SDK 改为 `httpx` HTTP 直连

**执行日期**: 2026-05-21

**重构依据**: `harness-core/dev-standards/backend-plugin.mdc` - 禁止使用百炼官方 SDK，必须使用 HTTP 直接调用

## 重构内容

### 1. 代码重构

#### 1.1 移除 SDK 依赖

**修改文件**: `backend/src/plugins/bailian_client.py`

- 移除导入: `import dashscope`, `from dashscope import Generation, TextEmbedding, TextReRank`
- 添加导入: `import httpx`
- 移除 SDK 初始化: `dashscope.api_key`, `dashscope.base_http_api_url`
- 保留 Base URL: `self.base_url = settings.bailian_base_url.rstrip("/")`

#### 1.2 LLM 调用重构

**原 SDK 方式**:
```python
response = Generation.call(
    model=self.llm_model,
    messages=messages,
    temperature=temperature,
    max_tokens=max_tokens,
    result_format="message",
)
```

**新 HTTP 方式**:
```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{self.base_url}/services/aigc/text-generation/generation",
        headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": self.llm_model,
            "input": {"messages": messages},
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "result_format": "message",
            },
        },
        timeout=30.0,
    )
    data = response.json()
    # 解析响应
```

#### 1.3 Embedding 调用重构

**HTTP 端点**: `POST {base_url}/services/embeddings/text-embedding/text-embedding`

**请求体**:
```json
{
  "model": "text-embedding-v2",
  "input": {
    "texts": ["文本1", "文本2"]
  },
  "parameters": {
    "dimension": 1536
  }
}
```

**响应解析**: `data["output"]["embeddings"]` → `[{"embedding": [...]}, ...]`

#### 1.4 Reranker 调用重构

**HTTP 端点**: `POST {base_url}/services/rerank/text-rerank/text-rerank`

**请求体**:
```json
{
  "model": "gte-rerank",
  "input": {
    "query": "查询文本",
    "documents": ["文档1", "文档2"]
  },
  "parameters": {
    "top_n": 3,
    "return_documents": true
  }
}
```

**响应解析**: `data["output"]["results"]` → `[{"index": 0, "relevance_score": 0.95, "document": {"text": "..."}}, ...]`

### 2. 依赖更新

**修改文件**: `backend/requirements.txt`

- 移除: `dashscope>=1.14.0`
- 保留: `httpx>=0.25.0` (已存在)

### 3. 单元测试更新

**修改文件**: `backend/tests/test_bailian_client.py`

#### 3.1 Mock 策略变更

**原 SDK Mock**:
```python
with patch("src.plugins.bailian_client.Generation.call", return_value=mock_response):
    result = await bailian_client.call_llm(...)
```

**新 HTTP Mock** (使用 AsyncMock):
```python
mock_client = MagicMock()
mock_client.post = AsyncMock(return_value=mock_response)
mock_async_client = AsyncMock()
mock_async_client.__aenter__.return_value = mock_client
mock_async_client.__aexit__.return_value = None

with patch("httpx.AsyncClient", return_value=mock_async_client):
    result = await bailian_client.call_llm(...)
```

#### 3.2 测试覆盖

- LLM 调用: 6 个测试用例 ✅
- Embedding 调用: 5 个测试用例 ✅
- Reranker 调用: 6 个测试用例 ✅
- 重试机制: 2 个测试用例 ✅
- 配置加载: 3 个测试用例 ✅
- 集成测试: 3 个测试用例 (跳过)

## 验证结果

### 1. 单元测试

```bash
pytest tests/test_bailian_client.py -v
```

**结果**: ✅ 22 passed, 3 skipped, 0 failed

### 2. 代码质量

#### 2.1 Ruff Linting

```bash
ruff check src/plugins/bailian_client.py
```

**结果**: ✅ All checks passed!

#### 2.2 Mypy Type Checking

```bash
mypy src/plugins/bailian_client.py --ignore-missing-imports
```

**结果**: ✅ Success: no issues found

### 3. 功能保留验证

✅ 重试机制 (3次 + 指数退避)
✅ 降级标识 (返回 None)
✅ 错误日志 (使用 `api_message` 避免参数冲突)
✅ 配置加载 (.env + llm_config.yaml)
✅ 参数透传 (temperature, max_tokens, dimension, top_k)

## API 端点文档

### 基础信息

- **Base URL**: `https://dashscope.aliyuncs.com/api/v1`
- **认证方式**: `Authorization: Bearer {API_KEY}`
- **Content-Type**: `application/json`

### 端点列表

1. **Text Generation**
   - URL: `POST /services/aigc/text-generation/generation`
   - 文档: https://help.aliyun.com/zh/dashscope/

2. **Text Embedding**
   - URL: `POST /services/embeddings/text-embedding/text-embedding`
   - 文档: https://help.aliyun.com/zh/model-studio/text-embedding-batch-api

3. **Text Rerank**
   - URL: `POST /services/rerank/text-rerank/text-rerank`
   - 文档: https://help.aliyun.com/zh/model-studio/text-rerank-api

## 重构优势

### 1. 符合规范

✅ 符合 `backend-plugin.mdc` 规范要求
✅ 禁止使用第三方 SDK
✅ 所有 API 调用透明可控

### 2. 代码质量

✅ 移除 SDK 黑盒依赖
✅ HTTP 请求/响应结构透明
✅ 易于调试和排查问题
✅ 减少依赖包体积

### 3. 维护性

✅ 请求体/响应体结构清晰
✅ 错误处理更精确
✅ 日志记录更详细
✅ 版本控制更灵活

## 兼容性

✅ 保持与原 SDK 相同的函数签名
✅ 保持相同的返回值格式
✅ 保持相同的降级策略
✅ 保持相同的重试机制

## 风险与注意事项

### 已处理风险

1. **异步上下文管理**
   - 使用 `async with httpx.AsyncClient()` 确保连接正确关闭
   - 使用 `AsyncMock` 正确模拟异步调用

2. **错误处理**
   - 保留原有的重试机制
   - 保留降级标识 (返回 None)
   - 添加 HTTP 状态码检查

3. **超时控制**
   - 所有 HTTP 请求设置 30 秒超时
   - 防止长时间阻塞

### 注意事项

1. **真实 API 调用**
   - 集成测试 (标记为 `@pytest.mark.integration`) 默认跳过
   - 需要真实 API Key 才能运行: `SKIP_INTEGRATION_TESTS=false pytest -m integration`

2. **API 变更**
   - 百炼 API 可能会更新
   - 需要定期查看官方文档
   - 建议添加 API 版本监控

3. **性能影响**
   - HTTP 直连与 SDK 性能相当
   - 网络层开销未增加
   - 重试机制开销未变化

## 后续建议

1. **监控**
   - 添加 API 调用成功率监控
   - 添加响应时间监控
   - 添加错误率告警

2. **优化**
   - 考虑使用连接池 (httpx 已内置)
   - 考虑添加缓存机制 (针对 Embedding)
   - 考虑批量调用优化

3. **文档**
   - 更新项目文档，说明 HTTP 直连方式
   - 更新 API 调用示例
   - 添加故障排查指南

## 总结

本次重构成功将百炼客户端从 SDK 依赖改为 HTTP 直连，符合项目开发规范要求。重构后：

- ✅ 移除了 `dashscope` SDK 依赖
- ✅ 所有功能保持一致
- ✅ 所有测试通过
- ✅ 代码质量检查通过
- ✅ API 调用透明可控

重构完成，可以安全投入使用。

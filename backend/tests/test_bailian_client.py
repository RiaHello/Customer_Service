"""
BailianClient 单元测试

测试场景：
1. LLM 调用（正常、失败、降级）
2. Embedding 调用（正常、失败、降级）
3. Reranker 调用（正常、失败、降级）
4. 配置加载（环境变量、YAML 文件）
5. 重试机制（3次重试、指数退避）

注意：重构为 HTTP 直连后，使用 httpx Mock 替代 SDK Mock
"""
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml

from src.plugins.bailian_client import BailianClient


@pytest.fixture
def mock_config():
    """Mock 配置文件"""
    return {
        "llm": {"model": "qwen-plus", "temperature": 0.7, "max_tokens": 2000, "top_p": 0.9},
        "embedding": {"model": "text-embedding-v2", "dimension": 1536},
        "reranker": {"model": "gte-rerank", "top_k": 3},
        "retry": {"max_retries": 3, "retry_delay": 0.1, "backoff_factor": 2.0},
    }


@pytest.fixture
def mock_settings():
    """Mock settings"""
    with patch("src.plugins.bailian_client.settings") as mock_settings:
        mock_settings.bailian_api_key = "sk-test-key"
        mock_settings.bailian_base_url = "https://dashscope.aliyuncs.com/api/v1/"
        mock_settings.bailian_llm_model = "qwen-plus"
        mock_settings.bailian_embedding_model = "text-embedding-v2"
        mock_settings.bailian_reranker_model = "gte-rerank"
        yield mock_settings


@pytest.fixture
def bailian_client(mock_settings, mock_config):
    """创建 BailianClient 实例（Mock 配置文件）"""
    config_yaml = yaml.dump(mock_config)

    def mock_open_func(*args, **kwargs):
        from io import StringIO

        return StringIO(config_yaml)

    with patch("builtins.open", mock_open_func):
        with patch("pathlib.Path.exists", return_value=True):
            client = BailianClient()
    return client


class TestBailianClientInit:
    """测试初始化"""

    def test_init_success(self, mock_settings, mock_config):
        """测试初始化成功"""
        config_yaml = yaml.dump(mock_config)

        def mock_open_func(*args, **kwargs):
            from io import StringIO

            return StringIO(config_yaml)

        with patch("builtins.open", mock_open_func):
            with patch("pathlib.Path.exists", return_value=True):
                client = BailianClient()

        assert client.api_key == "sk-test-key"
        assert client.llm_model == "qwen-plus"
        assert client.embedding_model == "text-embedding-v2"
        assert client.reranker_model == "gte-rerank"
        assert client.max_retries == 3

    def test_init_missing_api_key(self, mock_config):
        """测试 API Key 缺失"""
        with patch("src.plugins.bailian_client.settings") as mock_settings:
            mock_settings.bailian_api_key = ""
            with pytest.raises(ValueError, match="BAILIAN_API_KEY is required"):
                BailianClient()

    def test_init_config_file_not_found(self, mock_settings):
        """测试配置文件不存在时使用默认配置"""
        with patch("pathlib.Path.exists", return_value=False):
            client = BailianClient()

        assert client.llm_model == "qwen-plus"
        assert client.embedding_model == "text-embedding-v2"
        assert client.max_retries == 3


class TestLLMCall:
    """测试 LLM 调用"""

    @pytest.mark.asyncio
    async def test_call_llm_success(self, bailian_client):
        """测试 LLM 调用成功"""
        # Mock HTTP 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output": {
                "choices": [{"message": {"content": "这是 AI 的回答"}}],
                "usage": {"input_tokens": 10, "output_tokens": 5},
            }
        }

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_llm([{"role": "user", "content": "你好"}])

        assert result == "这是 AI 的回答"

    @pytest.mark.asyncio
    async def test_call_llm_with_custom_params(self, bailian_client):
        """测试 LLM 调用（自定义参数）"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output": {
                "choices": [{"message": {"content": "回答"}}],
                "usage": {},
            }
        }

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_llm([{"role": "user", "content": "测试"}], temperature=0.5, max_tokens=1000)

        assert result == "回答"
        # 验证请求参数
        call_args = mock_client.post.call_args
        request_body = call_args[1]["json"]
        assert request_body["parameters"]["temperature"] == 0.5
        assert request_body["parameters"]["max_tokens"] == 1000

    @pytest.mark.asyncio
    async def test_call_llm_no_choices(self, bailian_client):
        """测试 LLM 返回空 choices（触发降级）"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"output": {"choices": []}}

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_llm([{"role": "user", "content": "你好"}])

        assert result is None  # 降级标识

    @pytest.mark.asyncio
    async def test_call_llm_api_error(self, bailian_client):
        """测试 LLM API 错误（触发重试）"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"message": "Internal Server Error"}

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_llm([{"role": "user", "content": "你好"}])

        assert result is None  # 降级标识

    @pytest.mark.asyncio
    async def test_call_llm_exception(self, bailian_client):
        """测试 LLM 调用异常（触发重试）"""
        # Mock AsyncClient context manager to raise exception with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=Exception("Network error"))
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_llm([{"role": "user", "content": "你好"}])

        assert result is None  # 降级标识


class TestEmbeddingCall:
    """测试 Embedding 调用"""

    @pytest.mark.asyncio
    async def test_call_embedding_success(self, bailian_client):
        """测试 Embedding 调用成功"""
        # Mock HTTP 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output": {
                "embeddings": [
                    {"embedding": [0.1, 0.2, 0.3]},
                    {"embedding": [0.4, 0.5, 0.6]},
                ]
            }
        }

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_embedding(["文本1", "文本2"])

        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

    @pytest.mark.asyncio
    async def test_call_embedding_with_dimension(self, bailian_client):
        """测试 Embedding 调用（指定维度）"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"output": {"embeddings": [{"embedding": [0.1] * 1024}]}}

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_embedding(["文本"], dimension=1024)

        assert len(result[0]) == 1024
        # 验证请求参数
        call_args = mock_client.post.call_args
        request_body = call_args[1]["json"]
        assert request_body["parameters"]["dimension"] == 1024

    @pytest.mark.asyncio
    async def test_call_embedding_no_embeddings(self, bailian_client):
        """测试 Embedding 返回空结果（触发降级）"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"output": {"embeddings": []}}

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_embedding(["文本"])

        assert result is None  # 降级标识

    @pytest.mark.asyncio
    async def test_call_embedding_api_error(self, bailian_client):
        """测试 Embedding API 错误（触发重试）"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_response.json.return_value = {"message": "Rate limit exceeded"}

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_embedding(["文本"])

        assert result is None  # 降级标识

    @pytest.mark.asyncio
    async def test_call_embedding_exception(self, bailian_client):
        """测试 Embedding 调用异常（触发重试）"""
        # Mock AsyncClient context manager to raise exception with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=Exception("API error"))
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_embedding(["文本"])

        assert result is None  # 降级标识


class TestRerankerCall:
    """测试 Reranker 调用"""

    @pytest.mark.asyncio
    async def test_call_reranker_success(self, bailian_client):
        """测试 Reranker 调用成功"""
        # Mock HTTP 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output": {
                "results": [
                    {"index": 2, "relevance_score": 0.95, "document": {"text": "文档3"}},
                    {"index": 0, "relevance_score": 0.85, "document": {"text": "文档1"}},
                ]
            }
        }

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_reranker("查询", ["文档1", "文档2", "文档3"])

        assert len(result) == 2
        assert result[0]["index"] == 2
        assert result[0]["relevance_score"] == 0.95
        assert result[0]["document"] == "文档3"
        assert result[1]["index"] == 0
        assert result[1]["relevance_score"] == 0.85

    @pytest.mark.asyncio
    async def test_call_reranker_with_top_k(self, bailian_client):
        """测试 Reranker 调用（指定 top_k）"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output": {"results": [{"index": 0, "relevance_score": 0.9, "document": {"text": "文档1"}}]}
        }

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_reranker("查询", ["文档1", "文档2"], top_k=1)

        assert len(result) == 1
        # 验证请求参数
        call_args = mock_client.post.call_args
        request_body = call_args[1]["json"]
        assert request_body["parameters"]["top_n"] == 1

    @pytest.mark.asyncio
    async def test_call_reranker_without_documents(self, bailian_client):
        """测试 Reranker 调用（不返回文档内容）"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"output": {"results": [{"index": 0, "relevance_score": 0.9}]}}

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_reranker("查询", ["文档1"], return_documents=False)

        assert len(result) == 1
        assert "document" not in result[0]

    @pytest.mark.asyncio
    async def test_call_reranker_no_results(self, bailian_client):
        """测试 Reranker 返回空结果（触发降级）"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"output": {"results": []}}

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_reranker("查询", ["文档1"])

        assert result is None  # 降级标识

    @pytest.mark.asyncio
    async def test_call_reranker_api_error(self, bailian_client):
        """测试 Reranker API 错误（触发重试）"""
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.text = "Service unavailable"
        mock_response.json.return_value = {"message": "Service unavailable"}

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_reranker("查询", ["文档1"])

        assert result is None  # 降级标识

    @pytest.mark.asyncio
    async def test_call_reranker_exception(self, bailian_client):
        """测试 Reranker 调用异常（触发重试）"""
        # Mock AsyncClient context manager to raise exception with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=Exception("Timeout"))
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_reranker("查询", ["文档1"])

        assert result is None  # 降级标识


class TestRetryMechanism:
    """测试重试机制"""

    @pytest.mark.asyncio
    async def test_retry_count(self, bailian_client):
        """测试重试次数（应该重试 3 次）"""
        call_count = 0

        async def mock_post_func(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Error"
            mock_response.json.return_value = {"message": "Error"}
            return mock_response

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=mock_post_func)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_llm([{"role": "user", "content": "测试"}])

        assert result is None
        assert call_count == 3  # 初次调用 + 2次重试 = 3次

    @pytest.mark.asyncio
    async def test_retry_success_on_second_attempt(self, bailian_client):
        """测试第二次重试成功"""
        call_count = 0

        async def mock_post_func(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_response = MagicMock()
            if call_count < 2:
                mock_response.status_code = 500
                mock_response.text = "Temporary error"
                mock_response.json.return_value = {"message": "Temporary error"}
            else:
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "output": {
                        "choices": [{"message": {"content": "成功"}}],
                        "usage": {},
                    }
                }
            return mock_response

        # Mock AsyncClient context manager with AsyncMock
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=mock_post_func)
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_client
        mock_async_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await bailian_client.call_llm([{"role": "user", "content": "测试"}])

        assert result == "成功"
        assert call_count == 2  # 第一次失败，第二次成功


class TestBasePluginIntegration:
    """测试 BasePlugin 集成"""

    @pytest.mark.asyncio
    async def test_execute_not_supported(self, bailian_client):
        """测试 execute 方法（不支持）"""
        result = await bailian_client.execute()
        assert not result  # PluginResult 失败
        assert "does not support execute()" in result.error


# 可选：真实 API 联调测试（需要真实 API Key）
@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("SKIP_INTEGRATION_TESTS", "true").lower() == "true",
    reason="Integration tests skipped by default. Set SKIP_INTEGRATION_TESTS=false to run.",
)
class TestRealAPIIntegration:
    """真实 API 联调测试（可选）

    运行方式：SKIP_INTEGRATION_TESTS=false pytest -v -m integration backend/tests/test_bailian_client.py
    前提：.env 中配置真实 BAILIAN_API_KEY
    """

    @pytest.mark.asyncio
    async def test_real_llm_call(self, bailian_client):
        """测试真实 LLM 调用"""
        result = await bailian_client.call_llm([{"role": "user", "content": "你好，请简单回复"}])
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_real_embedding_call(self, bailian_client):
        """测试真实 Embedding 调用"""
        result = await bailian_client.call_embedding(["测试文本"])
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert len(result[0]) == 1536  # text-embedding-v2 默认维度

    @pytest.mark.asyncio
    async def test_real_reranker_call(self, bailian_client):
        """测试真实 Reranker 调用"""
        result = await bailian_client.call_reranker("电脑故障", ["电脑无法开机", "网络连接问题", "打印机故障"])
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        assert "relevance_score" in result[0]

"""
阿里云百炼平台客户端封装

功能：
- LLM 调用（文本生成）
- Embedding 调用（向量生成）
- Reranker 调用（结果重排）

特性：
- 使用 httpx 直接发送 HTTP 请求（符合 backend-plugin.mdc 规范）
- 配置从环境变量和 YAML 文件加载
- API 调用失败时重试 3 次
- 最终失败返回降级标识
- 记录错误日志
"""
import asyncio
from pathlib import Path
from typing import Any

import httpx
import yaml
from pycore.core import get_logger
from pycore.plugins import BasePlugin, PluginResult

from src.core.config import settings

logger = get_logger()


class BailianClient(BasePlugin):
    """
    阿里云百炼平台客户端

    使用 pycore.plugins.BasePlugin 基类实现。
    """

    name: str = "bailian_client"
    description: str = "阿里云百炼平台客户端，支持 LLM、Embedding、Reranker 调用"
    parameters: dict[str, Any] = {}

    def __init__(self) -> None:
        """
        初始化百炼客户端

        配置加载顺序：
        1. 从 backend/.env 读取 API Key 和 Base URL
        2. 从 backend/config/llm_config.yaml 读取模型配置
        """
        super().__init__()

        # 从环境变量加载 API Key 和 Base URL
        self.api_key = settings.bailian_api_key
        if not self.api_key:
            logger.error("BAILIAN_API_KEY not found in environment variables")
            raise ValueError("BAILIAN_API_KEY is required")

        # 设置 Base URL（移除 SDK 依赖）
        self.base_url = settings.bailian_base_url.rstrip("/")

        # 加载 YAML 配置文件
        config_path = Path(__file__).resolve().parent.parent.parent / "config" / "llm_config.yaml"
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using default config")
            self.config = self._default_config()
        else:
            with open(config_path, encoding="utf-8") as f:
                self.config = yaml.safe_load(f)

        # 模型配置
        self.llm_model = self.config.get("llm", {}).get("model", settings.bailian_llm_model)
        self.embedding_model = self.config.get("embedding", {}).get("model", settings.bailian_embedding_model)
        self.reranker_model = self.config.get("reranker", {}).get("model", settings.bailian_reranker_model)

        # 重试配置
        self.max_retries = self.config.get("retry", {}).get("max_retries", 3)
        self.retry_delay = self.config.get("retry", {}).get("retry_delay", 1.0)
        self.backoff_factor = self.config.get("retry", {}).get("backoff_factor", 2.0)

        logger.info(
            "BailianClient initialized (HTTP mode)",
            base_url=self.base_url,
            llm_model=self.llm_model,
            embedding_model=self.embedding_model,
            reranker_model=self.reranker_model,
        )

    def _default_config(self) -> dict[str, Any]:
        """返回默认配置"""
        return {
            "llm": {
                "model": "qwen-plus",
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9,
            },
            "embedding": {
                "model": "text-embedding-v2",
                "dimension": 1536,
            },
            "reranker": {
                "model": "gte-rerank",
                "top_k": 3,
            },
            "retry": {
                "max_retries": 3,
                "retry_delay": 1.0,
                "backoff_factor": 2.0,
            },
        }

    async def execute(self, **kwargs: Any) -> PluginResult:
        """
        BasePlugin 要求实现的 execute 方法

        本客户端不使用 execute，而是直接调用 call_llm、call_embedding、call_reranker
        """
        return self.fail("BailianClient does not support execute(), use call_llm/call_embedding/call_reranker instead")

    async def call_llm(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str | None:
        """
        调用 LLM 生成文本（HTTP 直连）

        Args:
            messages: 对话消息列表，格式：[{"role": "user", "content": "..."}]
            temperature: 温度参数（0-1），默认使用配置文件值
            max_tokens: 最大生成 token 数，默认使用配置文件值
            **kwargs: 其他参数

        Returns:
            str | None: 生成的文本，失败返回 None（触发降级）

        降级标识：
            - 返回 None 表示需要降级处理（如使用关键词回退）
        """
        llm_config = self.config.get("llm", {})
        temperature = temperature or llm_config.get("temperature", 0.7)
        max_tokens = max_tokens or llm_config.get("max_tokens", 2000)

        # 构造请求体
        request_body = {
            "model": self.llm_model,
            "input": {"messages": messages},
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "result_format": "message",
            },
        }

        for attempt in range(self.max_retries):
            try:
                # 发送 HTTP POST 请求
                async with httpx.AsyncClient(trust_env=False) as client:
                    response = await client.post(
                        f"{self.base_url}/services/aigc/text-generation/generation",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json=request_body,
                        timeout=30.0,
                    )

                    # 解析响应
                    if response.status_code == 200:
                        data = response.json()
                        output = data.get("output", {})
                        choices = output.get("choices", [])
                        if choices:
                            content: str = choices[0].get("message", {}).get("content", "")
                            usage = output.get("usage", {})
                            logger.info(
                                "LLM call succeeded",
                                model=self.llm_model,
                                input_tokens=usage.get("input_tokens"),
                                output_tokens=usage.get("output_tokens"),
                            )
                            return content
                        logger.warning("LLM response has no choices", response_data=data)
                        return None
                    else:
                        # API 错误
                        error_data = response.json() if response.text else {}
                        logger.warning(
                            "LLM call failed",
                            status_code=response.status_code,
                            api_message=error_data.get("message", response.text),
                            attempt=attempt + 1,
                        )

            except Exception as e:
                logger.error("LLM call exception", error=str(e), attempt=attempt + 1)

            # 重试前等待（指数退避）
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (self.backoff_factor**attempt)
                logger.info(f"Retrying LLM call in {delay:.1f}s...")
                await asyncio.sleep(delay)

        # 最终失败，返回降级标识
        logger.error("LLM call failed after all retries", max_retries=self.max_retries)
        return None

    async def call_embedding(self, texts: list[str], dimension: int | None = None) -> list[list[float]] | None:
        """
        调用 Embedding 生成向量（HTTP 直连）

        Args:
            texts: 文本列表
            dimension: 向量维度（可选），默认使用配置文件值

        Returns:
            list[list[float]] | None: 向量列表，失败返回 None（触发降级）

        降级标识：
            - 返回 None 表示需要降级处理（如使用关键词检索）
        """
        embedding_config = self.config.get("embedding", {})
        dimension = dimension or embedding_config.get("dimension")

        # 构造请求体
        request_body = {
            "model": self.embedding_model,
            "input": {"texts": texts},
        }
        if dimension:
            request_body["parameters"] = {"dimension": dimension}

        for attempt in range(self.max_retries):
            try:
                # 发送 HTTP POST 请求
                async with httpx.AsyncClient(trust_env=False) as client:
                    response = await client.post(
                        f"{self.base_url}/services/embeddings/text-embedding/text-embedding",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json=request_body,
                        timeout=30.0,
                    )

                    # 解析响应
                    if response.status_code == 200:
                        data = response.json()
                        output = data.get("output", {})
                        embeddings_data = output.get("embeddings", [])
                        if embeddings_data:
                            embeddings = [item["embedding"] for item in embeddings_data]
                            logger.info(
                                "Embedding call succeeded",
                                model=self.embedding_model,
                                text_count=len(texts),
                                dimension=len(embeddings[0]) if embeddings else None,
                            )
                            return embeddings
                        logger.warning("Embedding response has no embeddings", response_data=data)
                        return None
                    else:
                        # API 错误
                        error_data = response.json() if response.text else {}
                        logger.warning(
                            "Embedding call failed",
                            status_code=response.status_code,
                            api_message=error_data.get("message", response.text),
                            attempt=attempt + 1,
                        )

            except Exception as e:
                logger.error("Embedding call exception", error=str(e), attempt=attempt + 1)

            # 重试前等待（指数退避）
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (self.backoff_factor**attempt)
                logger.info(f"Retrying Embedding call in {delay:.1f}s...")
                await asyncio.sleep(delay)

        # 最终失败，返回降级标识
        logger.error("Embedding call failed after all retries", max_retries=self.max_retries)
        return None

    async def call_reranker(
        self, query: str, documents: list[str], top_k: int | None = None, return_documents: bool = True
    ) -> list[dict[str, Any]] | None:
        """
        调用 Reranker 重排文档（HTTP 直连）

        Args:
            query: 查询文本
            documents: 候选文档列表
            top_k: 返回前 K 个结果，默认使用配置文件值
            return_documents: 是否返回文档内容

        Returns:
            list[dict] | None: 重排结果列表，格式：[{"index": 0, "relevance_score": 0.95, "document": "..."}]
                               失败返回 None（触发降级）

        降级标识：
            - 返回 None 表示需要降级处理（如跳过重排，直接使用 RRF Top-3）
        """
        reranker_config = self.config.get("reranker", {})
        top_k = top_k or reranker_config.get("top_k", 3)

        # 构造请求体
        request_body = {
            "model": self.reranker_model,
            "input": {
                "query": query,
                "documents": documents,
            },
            "parameters": {
                "top_n": top_k,
                "return_documents": return_documents,
            },
        }

        for attempt in range(self.max_retries):
            try:
                # 发送 HTTP POST 请求
                async with httpx.AsyncClient(trust_env=False) as client:
                    response = await client.post(
                        f"{self.base_url}/services/rerank/text-rerank/text-rerank",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json=request_body,
                        timeout=30.0,
                    )

                    # 解析响应
                    if response.status_code == 200:
                        data = response.json()
                        output = data.get("output", {})
                        results_data = output.get("results", [])
                        if results_data:
                            results = []
                            for item in results_data:
                                result = {
                                    "index": item.get("index", 0),
                                    "relevance_score": item.get("relevance_score", 0.0),
                                }

                                if return_documents:
                                    # 从字典中提取 document 字段
                                    document_dict = item.get("document")
                                    if document_dict:
                                        # document 是一个包含 text 字段的字典
                                        if isinstance(document_dict, dict) and "text" in document_dict:
                                            result["document"] = document_dict["text"]
                                        else:
                                            result["document"] = str(document_dict)
                                    else:
                                        result["document"] = ""

                                results.append(result)
                            logger.info(
                                "Reranker call succeeded",
                                model=self.reranker_model,
                                query_length=len(query),
                                document_count=len(documents),
                                top_k=top_k,
                                result_count=len(results),
                            )
                            return results
                        logger.warning("Reranker response has no results", response_data=data)
                        return None
                    else:
                        # API 错误
                        error_data = response.json() if response.text else {}
                        logger.warning(
                            "Reranker call failed",
                            status_code=response.status_code,
                            api_message=error_data.get("message", response.text),
                            attempt=attempt + 1,
                        )

            except Exception as e:
                logger.error("Reranker call exception", error=str(e), attempt=attempt + 1)

            # 重试前等待（指数退避）
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (self.backoff_factor**attempt)
                logger.info(f"Retrying Reranker call in {delay:.1f}s...")
                await asyncio.sleep(delay)

        # 最终失败，返回降级标识
        logger.error("Reranker call failed after all retries", max_retries=self.max_retries)
        return None

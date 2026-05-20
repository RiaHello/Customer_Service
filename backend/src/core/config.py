"""
Application Configuration using ConfigManager + pydantic-settings.

混合方案：
1. 使用 pydantic_settings.BaseSettings 从 .env 文件加载配置
2. 将配置字典传递给 ConfigManager.load_from_dict()
3. 通过 ConfigManager 管理配置实例
"""
from pathlib import Path

from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict

from pycore.core import BaseSettings, ConfigManager


class AppSettings(BaseSettings):
    """
    Application Settings

    继承自 pycore.core.BaseSettings 以便与 ConfigManager 集成。
    """

    # 阿里云百炼平台配置
    bailian_api_key: str
    bailian_base_url: str = "https://dashscope.aliyuncs.com/api/v1/"
    bailian_llm_model: str = "qwen-plus"
    bailian_embedding_model: str = "text-embedding-v2"
    bailian_reranker_model: str = "gte-rerank"

    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./smart_customer_service.db"

    # JWT 配置
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440

    # RAG 配置
    rag_similarity_threshold: float = 0.8
    rag_top_k: int = 10
    rag_rrf_k: int = 60
    rag_rerank_top_k: int = 3

    # 服务配置
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    debug: bool = True


class _EnvLoader(PydanticBaseSettings):
    """
    临时加载器，用于从 .env 文件读取配置。

    使用 pydantic_settings.BaseSettings 以支持 .env 文件自动加载。
    """

    # 阿里云百炼平台配置
    bailian_api_key: str
    bailian_base_url: str = "https://dashscope.aliyuncs.com/api/v1/"
    bailian_llm_model: str = "qwen-plus"
    bailian_embedding_model: str = "text-embedding-v2"
    bailian_reranker_model: str = "gte-rerank"

    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./smart_customer_service.db"

    # JWT 配置
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440

    # RAG 配置
    rag_similarity_threshold: float = 0.8
    rag_top_k: int = 10
    rag_rrf_k: int = 60
    rag_rerank_top_k: int = 3

    # 服务配置
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    debug: bool = True

    model_config = SettingsConfigDict(
        # .env 文件路径：从 backend/src/core/config.py 到 backend/.env
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# 步骤1：使用 pydantic_settings 加载 .env
_temp_settings = _EnvLoader()  # type: ignore[call-arg]

# 步骤2：通过 ConfigManager 管理
config = ConfigManager[AppSettings]()
config.load_from_dict(AppSettings, _temp_settings.model_dump())

# 步骤3：导出 settings
settings = config.settings

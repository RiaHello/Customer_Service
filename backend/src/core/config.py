"""Application Configuration using PyCore"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application Settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # 阿里云百炼平台配置
    bailian_api_key: str = ""
    bailian_base_url: str = "https://dashscope.aliyuncs.com/api/v1/"
    bailian_llm_model: str = "qwen-plus"
    bailian_embedding_model: str = "text-embedding-v2"
    bailian_reranker_model: str = "gte-rerank"
    
    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./smart_customer_service.db"
    
    # JWT 配置
    jwt_secret_key: str = "your-secret-key-change-in-production"
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


# 全局配置实例
settings = Settings()

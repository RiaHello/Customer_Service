"""数据库会话管理
基于 pycore/integrations/db/session.py 模板扩展
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.db.models import Base

# 创建异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

# 创建异步会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """初始化数据库表结构"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库引擎"""
    await engine.dispose()

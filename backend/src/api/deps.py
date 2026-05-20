"""依赖注入模块
基于 pycore/api/deps.py 模板扩展
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

# from src.db.session import async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    数据库会话依赖注入

    Yields:
        AsyncSession: 异步数据库会话

    注意：当前为骨架实现，待数据库初始化后启用
    """
    # async with async_session() as session:
    #     try:
    #         yield session
    #         await session.commit()
    #     except Exception:
    #         await session.rollback()
    #         raise
    raise NotImplementedError("数据库会话暂未初始化，请先完成 B00-1 数据库初始化任务")

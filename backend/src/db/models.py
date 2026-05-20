"""数据库模型定义
基于 pycore/integrations/db/models.py 模板扩展
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy ORM 基类"""
    pass


# 示例模型（待数据库初始化任务补充完整表结构）
class User(Base):
    """用户表"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="employee")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

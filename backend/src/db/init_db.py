"""数据库初始化脚本

创建所有数据库表并插入测试账号

运行方式：
    cd backend
    PYTHONPATH=.. python -m src.db.init_db
"""
import asyncio
import sys
from pathlib import Path

import bcrypt
from sqlalchemy import text

# 确保能导入项目模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config import settings
from src.db.models import Base
from src.db.session import engine


def hash_password(password: str) -> str:
    """使用 bcrypt 哈希密码"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def create_tables():
    """创建所有数据库表（幂等性：仅在表不存在时创建）"""
    print("开始创建数据库表...")
    async with engine.begin() as conn:
        # 只创建不存在的表（幂等性）
        await conn.run_sync(Base.metadata.create_all)
    print("✓ 数据库表创建完成")


async def create_test_users():
    """创建测试账号（幂等性：存在则跳过）"""
    print("\n开始创建测试账号...")

    # 测试账号定义
    test_users = [
        {
            "username": "employee1",
            "password": "password123",
            "nickname": "测试员工",
            "role": "employee"
        },
        {
            "username": "agent1",
            "password": "password123",
            "nickname": "测试坐席",
            "role": "agent"
        },
        {
            "username": "admin",
            "password": "admin123",
            "nickname": "系统管理员",
            "role": "admin"
        }
    ]

    async with engine.begin() as conn:
        for user in test_users:
            # 检查用户是否已存在
            result = await conn.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {"username": user["username"]}
            )
            existing = result.fetchone()

            if existing:
                print(f"⊙ 跳过已存在用户: {user['username']} ({user['role']})")
                continue

            password_hash = hash_password(user["password"])

            # 插入新用户
            await conn.execute(
                text("""
                    INSERT INTO users (username, password_hash, nickname, profile_domains, total_queries, role, created_at)
                    VALUES (:username, :password_hash, :nickname, :profile_domains, :total_queries, :role, datetime('now'))
                """),
                {
                    "username": user["username"],
                    "password_hash": password_hash,
                    "nickname": user["nickname"],
                    "profile_domains": "{}",
                    "total_queries": 0,
                    "role": user["role"]
                }
            )

            print(f"✓ 创建用户: {user['username']} ({user['role']}) - 密码: {user['password']}")

    print("\n✓ 测试账号创建完成")


async def verify_tables():
    """验证表是否创建成功"""
    print("\n开始验证表结构...")

    async with engine.connect() as conn:
        # 查询所有表
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        )
        tables = [row[0] for row in result.fetchall()]

        expected_tables = [
            "users",
            "tickets",
            "messages",
            "documents",
            "document_chunks",
            "qa_pairs",
            "vectors",
            "keywords",
            "user_profiles"
        ]

        print(f"\n数据库中的表（共 {len(tables)} 个）：")
        for table in tables:
            status = "✓" if table in expected_tables else "?"
            print(f"  {status} {table}")

        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            print(f"\n⚠ 缺失的表: {', '.join(missing_tables)}")
        else:
            print("\n✓ 所有核心表都已创建")

        # 验证用户数量
        result = await conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"\n✓ 测试账号数量: {user_count}")


async def init_database():
    """主初始化流程"""
    print("=" * 60)
    print("智能客服系统 - 数据库初始化")
    print("=" * 60)
    print(f"\n数据库 URL: {settings.database_url}")
    print(f"数据库文件: {settings.database_url.replace('sqlite+aiosqlite:///', '')}")

    try:
        # 步骤1：创建表
        await create_tables()

        # 步骤2：创建测试账号
        await create_test_users()

        # 步骤3：验证
        await verify_tables()

        print("\n" + "=" * 60)
        print("数据库初始化完成！")
        print("=" * 60)
        print("\n测试账号信息：")
        print("  员工账号: employee1 / password123")
        print("  坐席账号: agent1 / password123")
        print("  管理员账号: admin / admin123")
        print("\n注意：以上账号仅用于开发测试，生产环境请修改密码。")

    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())

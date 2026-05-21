"""数据库初始化集成测试

验证数据库表结构与 PRD 契约的一致性
"""
import bcrypt
import pytest
from sqlalchemy import text

from src.db.models import Base
from src.db.session import engine


@pytest.mark.asyncio
async def test_all_tables_created():
    """验证所有 9 张核心表都已创建"""
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        )
        tables = [row[0] for row in result.fetchall()]

    expected_tables = {
        "users",
        "tickets",
        "messages",
        "documents",
        "document_chunks",
        "qa_pairs",
        "vectors",
        "keywords",
        "user_profiles"
    }

    actual_tables = set(tables)
    assert expected_tables.issubset(actual_tables), f"缺少表: {expected_tables - actual_tables}"


@pytest.mark.asyncio
async def test_test_accounts_exist():
    """验证 3 个测试账号存在"""
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT username, role FROM users WHERE username IN ('employee1', 'agent1', 'admin') ORDER BY username")
        )
        users = result.fetchall()

    assert len(users) == 3, f"预期 3 个测试账号，实际: {len(users)}"

    expected_users = [
        ("admin", "admin"),
        ("agent1", "agent"),
        ("employee1", "employee"),
    ]

    for i, (username, role) in enumerate(expected_users):
        assert users[i][0] == username, f"用户名不匹配: {users[i][0]} != {username}"
        assert users[i][1] == role, f"角色不匹配: {users[i][1]} != {role}"


@pytest.mark.asyncio
async def test_password_bcrypt_hashed():
    """验证密码使用 bcrypt 哈希"""
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT username, password_hash FROM users WHERE username = 'employee1'")
        )
        user = result.fetchone()

    assert user is not None, "测试用户 employee1 不存在"
    password_hash = user[1]

    # 验证密码哈希格式
    assert password_hash.startswith("$2b$"), f"密码不是 bcrypt 哈希: {password_hash[:10]}"

    # 验证密码正确性
    assert bcrypt.checkpw(b"123456", password_hash.encode("utf-8")), "密码校验失败"


@pytest.mark.asyncio
async def test_users_table_prd_compliance():
    """验证 users 表字段与 PRD 7.1.1 一致"""
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA table_info(users)"))
        columns = {row[1]: row for row in result.fetchall()}

    # PRD 7.1.1 必需字段
    required_fields = ["id", "username", "password_hash", "nickname", "profile_domains", "total_queries", "role", "created_at", "updated_at"]

    for field in required_fields:
        assert field in columns, f"users 表缺少字段: {field}"

    # 验证 username 唯一约束
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA index_list(users)"))
        indexes = result.fetchall()
        unique_indexes = [idx for idx in indexes if idx[2] == 1]  # unique flag
        assert len(unique_indexes) > 0, "username 未设置唯一约束"


@pytest.mark.asyncio
async def test_tickets_table_prd_compliance():
    """验证 tickets 表字段与 PRD 7.1.2 一致"""
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA table_info(tickets)"))
        columns = {row[1]: row for row in result.fetchall()}

    # PRD 7.1.2 必需字段
    required_fields = ["id", "user_id", "assigned_agent_id", "status", "category", "intent_level1", "intent_level2", "created_at", "updated_at", "completed_at"]

    for field in required_fields:
        assert field in columns, f"tickets 表缺少字段: {field}"


@pytest.mark.asyncio
async def test_documents_table_prd_compliance():
    """验证 documents 表字段与 PRD 7.1.6 一致"""
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA table_info(documents)"))
        columns = {row[1]: row for row in result.fetchall()}

    # PRD 7.1.6 必需字段
    required_fields = ["id", "filename", "status", "uploaded_by", "chunk_count", "qa_pair_count", "created_at", "processed_at"]

    for field in required_fields:
        assert field in columns, f"documents 表缺少字段: {field}"


@pytest.mark.asyncio
async def test_document_chunks_table_prd_compliance():
    """验证 document_chunks 表字段与 PRD 一致"""
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA table_info(document_chunks)"))
        columns = {row[1]: row for row in result.fetchall()}

    # PRD 要求字段
    required_fields = ["id", "document_id", "content", "chunk_index", "metadata", "created_at"]

    for field in required_fields:
        assert field in columns, f"document_chunks 表缺少字段: {field}"


@pytest.mark.asyncio
async def test_qa_pairs_table_prd_compliance():
    """验证 qa_pairs 表字段与 PRD 7.1.7 一致"""
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA table_info(qa_pairs)"))
        columns = {row[1]: row for row in result.fetchall()}

    # PRD 7.1.7 必需字段
    required_fields = ["id", "doc_id", "question", "answer", "question_vector", "created_at"]

    for field in required_fields:
        assert field in columns, f"qa_pairs 表缺少字段: {field}"


@pytest.mark.asyncio
async def test_vectors_table_prd_compliance():
    """验证 vectors 表字段与 PRD 7.1.7 一致"""
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA table_info(vectors)"))
        columns = {row[1]: row for row in result.fetchall()}

    # PRD 7.1.7 必需字段
    required_fields = ["id", "doc_id", "chunk_id", "chunk_text", "chunk_vector", "metadata", "created_at"]

    for field in required_fields:
        assert field in columns, f"vectors 表缺少字段: {field}"


@pytest.mark.asyncio
async def test_keywords_table_prd_compliance():
    """验证 keywords 表字段与 PRD 7.1.7 一致"""
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA table_info(keywords)"))
        columns = {row[1]: row for row in result.fetchall()}

    # PRD 7.1.7 必需字段
    required_fields = ["id", "doc_id", "chunk_id", "chunk_text", "keywords", "created_at"]

    for field in required_fields:
        assert field in columns, f"keywords 表缺少字段: {field}"


@pytest.mark.asyncio
async def test_foreign_keys_exist():
    """验证外键约束存在"""
    async with engine.connect() as conn:
        # tickets 表外键
        result = await conn.execute(text("PRAGMA foreign_key_list(tickets)"))
        tickets_fks = result.fetchall()
        fk_columns = [row[3] for row in tickets_fks]  # column 3 is 'from' column
        assert "user_id" in fk_columns, "tickets.user_id 外键缺失"
        assert "assigned_agent_id" in fk_columns, "tickets.assigned_agent_id 外键缺失"

        # messages 表外键
        result = await conn.execute(text("PRAGMA foreign_key_list(messages)"))
        messages_fks = result.fetchall()
        fk_columns = [row[3] for row in messages_fks]
        assert "ticket_id" in fk_columns, "messages.ticket_id 外键缺失"

        # documents 表外键
        result = await conn.execute(text("PRAGMA foreign_key_list(documents)"))
        documents_fks = result.fetchall()
        fk_columns = [row[3] for row in documents_fks]
        assert "uploaded_by" in fk_columns, "documents.uploaded_by 外键缺失"


@pytest.mark.asyncio
async def test_users_default_values():
    """验证 users 表默认值"""
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT total_queries, profile_domains FROM users WHERE username = 'employee1'")
        )
        user = result.fetchone()

    assert user is not None, "测试用户 employee1 不存在"
    assert user[0] == 0, f"total_queries 默认值应为 0，实际: {user[0]}"
    assert user[1] == "{}", f"profile_domains 默认值应为 {{}}，实际: {user[1]}"


@pytest.mark.asyncio
async def test_idempotency():
    """验证初始化脚本的幂等性"""
    # 第一次执行：获取初始用户数
    async with engine.connect() as conn:
        result1 = await conn.execute(text("SELECT COUNT(*) FROM users"))
        count1 = result1.scalar()

    # 再次创建表（不应删除已有数据）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 第二次执行：验证用户数未减少
    async with engine.connect() as conn:
        result2 = await conn.execute(text("SELECT COUNT(*) FROM users"))
        count2 = result2.scalar()

    assert count2 == count1, f"重复执行后用户数变化: {count1} -> {count2}"

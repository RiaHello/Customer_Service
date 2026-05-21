"""
登录接口单元测试

测试用户登录功能的各种场景。
"""
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_login_success_employee():
    """测试员工账号登录成功"""
    response = client.post(
        "/api/auth/login",
        json={"username": "employee1", "password": "123456"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "success"
    assert "data" in data
    assert "token" in data["data"]
    assert data["data"]["token_type"] == "Bearer"
    assert "user" in data["data"]

    user = data["data"]["user"]
    assert user["username"] == "employee1"
    assert user["role"] == "employee"
    assert "user_id" in user
    assert "display_name" in user
    assert "created_at" in user


def test_login_success_agent():
    """测试坐席账号登录成功"""
    response = client.post(
        "/api/auth/login",
        json={"username": "agent1", "password": "123456"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["user"]["role"] == "agent"


def test_login_success_admin():
    """测试管理员账号登录成功"""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "123456"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["user"]["role"] == "admin"


def test_login_fail_user_not_found():
    """测试用户名不存在"""
    response = client.post(
        "/api/auth/login",
        json={"username": "nonexistent", "password": "123456"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["code"] == 1001
    assert "用户名或密码错误" in data["message"]


def test_login_fail_incorrect_password():
    """测试密码错误"""
    response = client.post(
        "/api/auth/login",
        json={"username": "employee1", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["code"] == 1001
    assert "用户名或密码错误" in data["message"]


def test_login_validation_empty_username():
    """测试空用户名（请求体验证）"""
    response = client.post(
        "/api/auth/login",
        json={"username": "", "password": "123456"},
    )

    # Pydantic 验证失败返回 422
    assert response.status_code == 422


def test_login_validation_empty_password():
    """测试空密码（请求体验证）"""
    response = client.post(
        "/api/auth/login",
        json={"username": "employee1", "password": ""},
    )

    # Pydantic 验证失败返回 422
    assert response.status_code == 422


def test_login_validation_missing_username():
    """测试缺少用户名字段"""
    response = client.post(
        "/api/auth/login",
        json={"password": "123456"},
    )

    # Pydantic 验证失败返回 422
    assert response.status_code == 422


def test_login_validation_missing_password():
    """测试缺少密码字段"""
    response = client.post(
        "/api/auth/login",
        json={"username": "employee1"},
    )

    # Pydantic 验证失败返回 422
    assert response.status_code == 422


def test_login_display_name_fallback():
    """测试用户昵称显示（有 nickname 则显示 nickname，否则显示 username）"""
    # employee1 有 nickname "测试员工"
    response = client.post(
        "/api/auth/login",
        json={"username": "employee1", "password": "123456"},
    )

    assert response.status_code == 200
    data = response.json()
    user = data["data"]["user"]
    assert user["display_name"] == "测试员工"  # 应显示 nickname


def test_login_token_contains_correct_claims():
    """测试返回的 Token 包含正确的用户信息"""
    from src.core.auth import verify_token

    response = client.post(
        "/api/auth/login",
        json={"username": "employee1", "password": "123456"},
    )

    assert response.status_code == 200
    data = response.json()
    token = data["data"]["token"]

    # 验证 Token
    payload = verify_token(token)
    assert payload["username"] == "employee1"
    assert payload["role"] == "employee"
    assert "user_id" in payload

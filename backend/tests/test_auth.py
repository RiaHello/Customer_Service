"""
JWT Token 认证功能测试

测试 JWT Token 生成、验证、过期场景和认证中间件。
"""
import time
from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.middleware.auth_middleware import AuthMiddleware
from src.core.auth import create_access_token, verify_token


class TestJWTToken:
    """JWT Token 生成与验证测试"""

    def test_create_access_token_success(self):
        """测试：成功创建 JWT Token"""
        # 创建 Token
        token = create_access_token(user_id=1, username="test_user", role="employee")

        # 验证 Token 格式（JWT 格式为 header.payload.signature）
        assert isinstance(token, str)
        assert len(token.split(".")) == 3

    def test_verify_token_success(self):
        """测试：成功验证有效 Token"""
        # 创建 Token
        token = create_access_token(user_id=1, username="test_user", role="employee")

        # 验证 Token
        payload = verify_token(token)

        # 检查载荷内容
        assert payload["user_id"] == 1
        assert payload["username"] == "test_user"
        assert payload["role"] == "employee"

    def test_verify_token_expired(self):
        """测试：验证过期 Token 返回 Token expired"""
        # 创建一个立即过期的 Token（过期时间为 -1 秒）
        token = create_access_token(
            user_id=1,
            username="test_user",
            role="employee",
            expires_delta=timedelta(seconds=-1),
        )

        # 等待 Token 过期
        time.sleep(0.1)

        # 验证过期 Token 应抛出 ValueError("Token expired")
        with pytest.raises(ValueError) as exc_info:
            verify_token(token)

        assert "expired" in str(exc_info.value).lower()

    def test_verify_token_invalid_signature(self):
        """测试：验证无效签名 Token 返回 Invalid token"""
        # 创建有效 Token
        token = create_access_token(user_id=1, username="test_user", role="employee")

        # 篡改 Token 签名（修改最后一个字符）
        invalid_token = token[:-1] + ("a" if token[-1] != "a" else "b")

        # 验证无效 Token 应抛出 ValueError("Invalid token")
        with pytest.raises(ValueError) as exc_info:
            verify_token(invalid_token)

        assert "invalid" in str(exc_info.value).lower()

    def test_verify_token_missing_claims(self):
        """测试：验证缺少必要字段的 Token"""
        from jose import jwt
        from src.core.config import settings

        # 手动创建一个缺少 username 字段的 Token
        payload = {"sub": "1", "role": "employee"}
        token = jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )

        # 验证缺少字段的 Token 应抛出 ValueError
        with pytest.raises(ValueError) as exc_info:
            verify_token(token)

        assert "missing required claims" in str(exc_info.value).lower()


class TestAuthMiddleware:
    """认证中间件测试"""

    @pytest.fixture
    def app(self):
        """创建测试用 FastAPI 应用"""
        app = FastAPI()

        # 注册认证中间件
        app.add_middleware(AuthMiddleware)

        # 注册测试路由
        @app.get("/health")
        def health():
            return {"status": "healthy"}

        @app.get("/api/auth/login")
        def login():
            return {"message": "login endpoint"}

        @app.get("/api/protected")
        def protected():
            return {"message": "protected endpoint"}

        return app

    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return TestClient(app)

    def test_whitelist_health_endpoint(self, client):
        """测试：/health 端点无需认证可访问"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_whitelist_login_endpoint(self, client):
        """测试：/api/auth/login 端点无需认证可访问"""
        response = client.get("/api/auth/login")
        assert response.status_code == 200
        assert response.json()["message"] == "login endpoint"

    def test_protected_endpoint_without_token(self, client):
        """测试：受保护端点无 Token 返回 401 Unauthorized"""
        response = client.get("/api/protected")
        assert response.status_code == 401
        assert response.json()["code"] == 401
        assert "unauthorized" in response.json()["message"].lower()

    def test_protected_endpoint_with_invalid_token(self, client):
        """测试：受保护端点使用无效 Token 返回 401 Invalid token"""
        response = client.get(
            "/api/protected", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        assert response.json()["code"] == 401
        assert "invalid token" in response.json()["message"].lower()

    def test_protected_endpoint_with_valid_token(self, client):
        """测试：受保护端点使用有效 Token 可访问"""
        # 创建有效 Token
        token = create_access_token(user_id=1, username="test_user", role="employee")

        # 访问受保护端点
        response = client.get(
            "/api/protected", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "protected endpoint"

    def test_protected_endpoint_with_expired_token(self, client):
        """测试：受保护端点使用过期 Token 返回 401 Token expired"""
        # 创建立即过期的 Token
        token = create_access_token(
            user_id=1,
            username="test_user",
            role="employee",
            expires_delta=timedelta(seconds=-1),
        )

        # 等待 Token 过期
        time.sleep(0.1)

        # 访问受保护端点
        response = client.get(
            "/api/protected", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert response.json()["code"] == 401
        assert "expired" in response.json()["message"].lower()

    def test_protected_endpoint_with_malformed_auth_header(self, client):
        """测试：受保护端点使用格式错误的 Authorization 头返回 401"""
        # 缺少 Bearer 前缀
        response = client.get(
            "/api/protected", headers={"Authorization": "invalid_token"}
        )
        assert response.status_code == 401

        # Authorization 头为空
        response = client.get("/api/protected", headers={"Authorization": ""})
        assert response.status_code == 401

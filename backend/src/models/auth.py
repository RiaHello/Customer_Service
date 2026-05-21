"""
认证相关的 Pydantic 模型

用于登录请求和响应的数据验证与序列化。
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求体"""

    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, max_length=128, description="密码")


class UserInfo(BaseModel):
    """用户信息"""

    user_id: int = Field(..., description="用户 ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")
    display_name: str = Field(..., description="显示名称")
    created_at: str = Field(..., description="创建时间")


class LoginResponse(BaseModel):
    """登录响应数据"""

    token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    user: UserInfo = Field(..., description="用户信息")

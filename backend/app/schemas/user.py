"""User-related Pydantic schemas.
用户相关的Pydantic模式

Defines request and response models for user registration,
authentication, and profile management.
定义用户注册、认证和资料管理的请求和响应模型。
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Schema for user registration requests.
    用户注册请求模式

    Attributes:
        username: Desired login name (3–50 characters).
        email: Valid email address.
        password: Plain-text password (6–128 characters); hashed before storage.
        display_name: Optional display name (max 100 characters).
    属性：
        username: 期望的登录名（3-50字符）
        email: 有效的电子邮件地址
        password: 明文密码（6-128字符）；存储前会被哈希
        display_name: 可选的显示名（最大100字符）
    """

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    display_name: str | None = Field(None, max_length=100)


class UserLoginRequest(BaseModel):
    """Schema for user login requests.
    用户登录请求模式

    Attributes:
        email: Registered email address.
        password: Plain-text password for verification.
    属性：
        email: 已注册的电子邮件地址
        password: 用于验证的明文密码
    """

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for JWT token responses returned after login or refresh.
    登录或刷新后返回的JWT令牌响应模式

    Attributes:
        access_token: Short-lived JWT access token.
        refresh_token: Long-lived JWT refresh token.
        token_type: Token type, always ``"bearer"``.
        user: The authenticated user's profile data.
    属性：
        access_token: 短期JWT访问令牌
        refresh_token: 长期JWT刷新令牌
        token_type: 令牌类型，始终为`"bearer"`
        user: 已认证用户的资料数据
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh requests.
    令牌刷新请求模式

    Attributes:
        refresh_token: The previously issued refresh token.
    属性：
        refresh_token: 先前颁发的刷新令牌
    """

    refresh_token: str


class UserResponse(BaseModel):
    """Schema for user profile responses.
    用户资料响应模式

    Attributes:
        id: Unique user identifier.
        username: Login name.
        email: Registered email address.
        display_name: Optional display name shown in the UI.
        avatar_url: Optional URL to the user's avatar image.
        created_at: Timestamp when the account was created.
    属性：
        id: 唯一用户标识符
        username: 登录名
        email: 已注册的电子邮件地址
        display_name: UI中显示的可选显示名
        avatar_url: 用户头像图片的可选URL
        created_at: 账户创建时间戳
    """

    id: uuid.UUID
    username: str
    email: str
    display_name: str | None
    avatar_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """Schema for user profile update requests.
    用户资料更新请求模式

    All fields are optional; only provided fields will be updated.
    所有字段都是可选的；只更新提供的字段。

    Attributes:
        display_name: New display name (max 100 characters).
        avatar_url: New avatar URL (max 500 characters).
    属性：
        display_name: 新的显示名（最大100字符）
        avatar_url: 新的头像URL（最大500字符）
    """

    display_name: str | None = Field(None, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)

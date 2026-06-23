"""Authentication service module. 认证服务模块

Provides user registration, login, JWT token refresh, and current-user
resolution. All JWT lifecycle concerns (creation, decoding, type validation)
are centralised here so that route handlers remain thin.

提供用户注册、登录、JWT令牌刷新和当前用户解析功能。所有JWT生命周期相关操作（创建、解码、类型验证）集中在此，使路由处理器保持简洁。
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)


class AuthService:
    """Service responsible for authentication and JWT token management.

    负责身份验证和JWT令牌管理的服务。

    Responsibilities:
        - Registering new users with duplicate-email/username checks.
        - Authenticating credentials and issuing JWT token pairs.
        - Refreshing expired access tokens via refresh-token rotation.
        - Resolving the current user from an access token.

    职责：
        - 注册新用户，检查重复邮箱/用户名
        - 验证凭据并颁发JWT令牌对
        - 通过刷新令牌轮换刷新过期的访问令牌
        - 从访问令牌解析当前用户
    """

    async def register(self, db: AsyncSession, data: UserRegisterRequest) -> TokenResponse:
        """Register a new user and return a fresh JWT token pair.

        注册新用户并返回新的JWT令牌对。

        Validates that the requested e-mail and username are not already taken,
        hashes the password, persists the user, and returns both an access
        token and a refresh token.

        验证请求的电子邮件和用户名未被占用，哈希密码，持久化用户，返回访问令牌和刷新令牌。

        Args:
            db: Async database session. 异步数据库会话
            data: Registration payload containing username, email, password,
                and display_name. 注册负载，包含用户名、邮箱、密码和显示名

        Returns:
            TokenResponse containing access_token, refresh_token, and the
            newly created user profile.
            包含access_token、refresh_token和新创建的用户资料

        Raises:
            ConflictException: If the email or username is already registered.
                              如果邮箱或用户名已被注册
        """
        existing = await db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise ConflictException("Email already registered")

        existing = await db.execute(select(User).where(User.username == data.username))
        if existing.scalar_one_or_none():
            raise ConflictException("Username already taken")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            display_name=data.display_name,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

        # Issue a new JWT access/refresh token pair for the registered user
        # 为注册用户颁发新的JWT访问/刷新令牌对
        user_id_str = str(user.id)
        access_token = create_access_token(user_id_str)
        refresh_token = create_refresh_token(user_id_str)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )

    async def login(self, db: AsyncSession, data: UserLoginRequest) -> TokenResponse:
        """Authenticate a user with email and password, returning JWT tokens.

        使用邮箱和密码认证用户，返回JWT令牌。

        Looks up the user by email and verifies the password hash. On success
        a new access/refresh token pair is issued.

        通过邮箱查找用户并验证密码哈希。成功后颁发新的访问/刷新令牌对。

        Args:
            db: Async database session. 异步数据库会话
            data: Login payload containing email and password. 登录负载，包含邮箱和密码

        Returns:
            TokenResponse containing access_token, refresh_token, and the
            authenticated user profile.
            包含access_token、refresh_token和已认证用户资料

        Raises:
            UnauthorizedException: If the email does not exist or the password
                is incorrect. 如果邮箱不存在或密码错误
        """
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        # Deliberately vague message to avoid user-enumeration attacks
        # 故意使用模糊消息以避免用户枚举攻击
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        # Issue a new JWT access/refresh token pair upon successful auth
        # 认证成功后颁发新的JWT访问/刷新令牌对
        user_id_str = str(user.id)
        access_token = create_access_token(user_id_str)
        refresh_token = create_refresh_token(user_id_str)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )

    async def refresh(self, refresh_token: str) -> dict:
        """Rotate a valid refresh token into a new access/refresh pair.

        将有效的刷新令牌轮换为新的访问/刷新令牌对。

        Decodes the provided refresh token, verifies its type claim is
        ``"refresh"``, and issues a fresh token pair for the same subject.

        解码提供的刷新令牌，验证其type声明为"refresh"，并为同一主题颁发新的令牌对。

        Args:
            refresh_token: The JWT refresh token submitted by the client.
                          客户端提交的JWT刷新令牌

        Returns:
            A dict with keys ``access_token``, ``refresh_token``, and
            ``token_type`` (always ``"bearer"``).
            包含access_token、refresh_token和token_type（始终为"bearer"）的字典

        Raises:
            UnauthorizedException: If the token cannot be decoded or its type
                claim is not ``"refresh"``. 如果令牌无法解码或其type声明不是"refresh"
        """
        try:
            payload = decode_token(refresh_token)
            # Ensure the token is actually a refresh token, not an access token
            # 确保令牌确实是刷新令牌，而不是访问令牌
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid refresh token")
        except ValueError as exc:
            raise UnauthorizedException("Invalid refresh token") from exc

        # Re-issue a new token pair for the same user (refresh-token rotation)
        # 为同一用户重新颁发令牌对（刷新令牌轮换）
        user_id = payload["sub"]
        new_access = create_access_token(user_id)
        new_refresh = create_refresh_token(user_id)

        return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}

    async def get_current_user(self, db: AsyncSession, token: str) -> User:
        """Validate an access token and return the corresponding User ORM object.

        验证访问令牌并返回相应的User ORM对象。

        Decodes the JWT, ensures its type claim is ``"access"``, looks up the
        user by the ``sub`` claim, and returns the full User model instance.

        解码JWT，确保其type声明为"access"，通过sub声明查找用户，并返回完整的User模型实例。

        Args:
            db: Async database session. 异步数据库会话
            token: The JWT access token from the Authorization header.
                   来自Authorization头的JWT访问令牌

        Returns:
            The authenticated User ORM instance. 已认证的User ORM实例

        Raises:
            UnauthorizedException: If the token is invalid, is not an access
                token, or the referenced user no longer exists.
                如果令牌无效、不是访问令牌或引用的用户不存在
        """
        try:
            payload = decode_token(token)
            # Reject refresh tokens used in place of access tokens
            # 拒绝将刷新令牌用作访问令牌
            if payload.get("type") != "access":
                raise UnauthorizedException("Invalid access token")
            user_id = payload["sub"]
        except ValueError as exc:
            raise UnauthorizedException("Invalid access token") from exc

        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        if not user:
            raise UnauthorizedException("User not found")

        return user


auth_service = AuthService()
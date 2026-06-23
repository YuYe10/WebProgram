"""Authentication endpoints.
认证端点

Provides user registration, login, token refresh, and profile
management routes for the v1 API.
为v1 API提供用户注册、登录、令牌刷新和资料管理路由。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services.auth import auth_service

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account.
    注册新用户账户

    Args:
        data: Registration payload containing email, username, and password.
              包含邮箱、用户名和密码的注册负载
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话

    Returns:
        TokenResponse: Access and refresh tokens for the newly created user.
                       新创建用户的访问令牌和刷新令牌

    Raises:
        ConflictException: If the email or username is already taken.
                          如果邮箱或用户名已被占用
    """
    return await auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password to receive access tokens.
    使用邮箱和密码登录以获取访问令牌

    Args:
        data: Login payload containing email and password.
              包含邮箱和密码的登录负载
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话

    Returns:
        TokenResponse: Access and refresh tokens upon successful authentication.
                       认证成功后的访问令牌和刷新令牌

    Raises:
        UnauthorizedException: If credentials are invalid.
                              如果凭据无效
    """
    return await auth_service.login(db, data)


@router.post("/refresh")
async def refresh(data: RefreshTokenRequest):
    """Refresh an expired access token.
    刷新过期的访问令牌

    Args:
        data: Payload containing the refresh token.
              包含刷新令牌的负载

    Returns:
        TokenResponse: New access and refresh tokens.
                       新的访问令牌和刷新令牌

    Raises:
        UnauthorizedException: If the refresh token is invalid or expired.
                              如果刷新令牌无效或过期
    """
    return await auth_service.refresh(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile.
    获取当前已认证用户的资料

    Args:
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户

    Returns:
        UserResponse: Profile data of the authenticated user.
                      已认证用户的资料数据
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile.
    更新当前用户的资料

    Only fields present in the request body (exclude_unset) are modified;
    omitted fields retain their existing values.
    只修改请求体中存在的字段（exclude_unset）；省略的字段保持其现有值。

    Args:
        data: Partial update payload with fields to change.
              包含要更改字段的部分更新负载
        current_user: Authenticated user resolved from the Bearer token.
                      从Bearer令牌解析的已认证用户
        db: Async database session injected via dependency.
            通过依赖注入的异步数据库会话

    Returns:
        UserResponse: Updated profile data of the authenticated user.
                      已认证用户的更新资料数据
    """
    # Apply only the fields that were explicitly set in the request
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    # Flush changes to DB and refresh the ORM instance with latest column values
    await db.flush()
    await db.refresh(current_user)
    return current_user

"""Authentication endpoints.

Provides user registration, login, token refresh, and profile
management routes for the v1 API.
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

    Args:
        data: Registration payload containing email, username, and password.
        db: Async database session injected via dependency.

    Returns:
        TokenResponse: Access and refresh tokens for the newly created user.

    Raises:
        ConflictException: If the email or username is already taken.
    """
    return await auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password to receive access tokens.

    Args:
        data: Login payload containing email and password.
        db: Async database session injected via dependency.

    Returns:
        TokenResponse: Access and refresh tokens upon successful authentication.

    Raises:
        UnauthorizedException: If credentials are invalid.
    """
    return await auth_service.login(db, data)


@router.post("/refresh")
async def refresh(data: RefreshTokenRequest):
    """Refresh an expired access token.

    Args:
        data: Payload containing the refresh token.

    Returns:
        TokenResponse: New access and refresh tokens.

    Raises:
        UnauthorizedException: If the refresh token is invalid or expired.
    """
    return await auth_service.refresh(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile.

    Args:
        current_user: Authenticated user resolved from the Bearer token.

    Returns:
        UserResponse: Profile data of the authenticated user.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile.

    Only fields present in the request body (exclude_unset) are modified;
    omitted fields retain their existing values.

    Args:
        data: Partial update payload with fields to change.
        current_user: Authenticated user resolved from the Bearer token.
        db: Async database session injected via dependency.

    Returns:
        UserResponse: Updated profile data of the authenticated user.
    """
    # Apply only the fields that were explicitly set in the request
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    # Flush changes to DB and refresh the ORM instance with latest column values
    await db.flush()
    await db.refresh(current_user)
    return current_user

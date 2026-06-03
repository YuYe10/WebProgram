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
    """Authentication service handling registration, login, and token management."""

    async def register(self, db: AsyncSession, data: UserRegisterRequest) -> TokenResponse:
        """Register a new user and return access tokens."""
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

        user_id_str = str(user.id)
        access_token = create_access_token(user_id_str)
        refresh_token = create_refresh_token(user_id_str)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )

    async def login(self, db: AsyncSession, data: UserLoginRequest) -> TokenResponse:
        """Authenticate a user and return access tokens."""
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        user_id_str = str(user.id)
        access_token = create_access_token(user_id_str)
        refresh_token = create_refresh_token(user_id_str)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )

    async def refresh(self, refresh_token: str) -> dict:
        """Refresh an access token using a valid refresh token."""
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid refresh token")
        except ValueError as exc:
            raise UnauthorizedException("Invalid refresh token") from exc

        user_id = payload["sub"]
        new_access = create_access_token(user_id)
        new_refresh = create_refresh_token(user_id)

        return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}

    async def get_current_user(self, db: AsyncSession, token: str) -> User:
        """Validate access token and return the current user."""
        try:
            payload = decode_token(token)
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

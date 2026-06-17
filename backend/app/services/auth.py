"""Authentication service module.

Provides user registration, login, JWT token refresh, and current-user
resolution.  All JWT lifecycle concerns (creation, decoding, type validation)
are centralised here so that route handlers remain thin.
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

    Responsibilities:
        - Registering new users with duplicate-email/username checks.
        - Authenticating credentials and issuing JWT token pairs.
        - Refreshing expired access tokens via refresh-token rotation.
        - Resolving the current user from an access token.
    """

    async def register(self, db: AsyncSession, data: UserRegisterRequest) -> TokenResponse:
        """Register a new user and return a fresh JWT token pair.

        Validates that the requested e-mail and username are not already taken,
        hashes the password, persists the user, and returns both an access
        token and a refresh token.

        Args:
            db: Async database session.
            data: Registration payload containing username, email, password,
                and display_name.

        Returns:
            TokenResponse containing access_token, refresh_token, and the
            newly created user profile.

        Raises:
            ConflictException: If the email or username is already registered.
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

        Looks up the user by email and verifies the password hash.  On success
        a new access/refresh token pair is issued.

        Args:
            db: Async database session.
            data: Login payload containing email and password.

        Returns:
            TokenResponse containing access_token, refresh_token, and the
            authenticated user profile.

        Raises:
            UnauthorizedException: If the email does not exist or the password
                is incorrect.
        """
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        # Deliberately vague message to avoid user-enumeration attacks
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        # Issue a new JWT access/refresh token pair upon successful auth
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

        Decodes the provided refresh token, verifies its type claim is
        ``"refresh"``, and issues a fresh token pair for the same subject.

        Args:
            refresh_token: The JWT refresh token submitted by the client.

        Returns:
            A dict with keys ``access_token``, ``refresh_token``, and
            ``token_type`` (always ``"bearer"``).

        Raises:
            UnauthorizedException: If the token cannot be decoded or its type
                claim is not ``"refresh"``.
        """
        try:
            payload = decode_token(refresh_token)
            # Ensure the token is actually a refresh token, not an access token
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid refresh token")
        except ValueError as exc:
            raise UnauthorizedException("Invalid refresh token") from exc

        # Re-issue a new token pair for the same user (refresh-token rotation)
        user_id = payload["sub"]
        new_access = create_access_token(user_id)
        new_refresh = create_refresh_token(user_id)

        return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}

    async def get_current_user(self, db: AsyncSession, token: str) -> User:
        """Validate an access token and return the corresponding User ORM object.

        Decodes the JWT, ensures its type claim is ``"access"``, looks up the
        user by the ``sub`` claim, and returns the full User model instance.

        Args:
            db: Async database session.
            token: The JWT access token from the Authorization header.

        Returns:
            The authenticated User ORM instance.

        Raises:
            UnauthorizedException: If the token is invalid, is not an access
                token, or the referenced user no longer exists.
        """
        try:
            payload = decode_token(token)
            # Reject refresh tokens used in place of access tokens
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

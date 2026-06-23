"""User-related Pydantic schemas.

Defines request and response models for user registration,
authentication, and profile management.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Schema for user registration requests.

    Attributes:
        username: Desired login name (3–50 characters).
        email: Valid email address.
        password: Plain-text password (6–128 characters); hashed before storage.
        display_name: Optional display name (max 100 characters).
    """

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    display_name: str | None = Field(None, max_length=100)


class UserLoginRequest(BaseModel):
    """Schema for user login requests.

    Attributes:
        email: Registered email address.
        password: Plain-text password for verification.
    """

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for JWT token responses returned after login or refresh.

    Attributes:
        access_token: Short-lived JWT access token.
        refresh_token: Long-lived JWT refresh token.
        token_type: Token type, always ``"bearer"``.
        user: The authenticated user's profile data.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh requests.

    Attributes:
        refresh_token: The previously issued refresh token.
    """

    refresh_token: str


class UserResponse(BaseModel):
    """Schema for user profile responses.

    Attributes:
        id: Unique user identifier.
        username: Login name.
        email: Registered email address.
        display_name: Optional display name shown in the UI.
        avatar_url: Optional URL to the user's avatar image.
        created_at: Timestamp when the account was created.
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

    All fields are optional; only provided fields will be updated.

    Attributes:
        display_name: New display name (max 100 characters).
        avatar_url: New avatar URL (max 500 characters).
    """

    display_name: str | None = Field(None, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)

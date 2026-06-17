"""Security utilities for password hashing and JWT token management.

Uses bcrypt for password hashing and python-jose (HS256) for
JSON Web Token creation and validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password: The password provided by the user.
        hashed_password: The stored bcrypt hash (as a string).

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        password: The plaintext password to hash.

    Returns:
        str: The bcrypt hash as a UTF-8 decoded string.
    """
    # rounds=12 provides a good balance of security and performance
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt(rounds=12)
    ).decode("utf-8")


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token.

    Args:
        subject: The token subject, typically the user ID.
        expires_delta: Custom expiration duration. Defaults to
            ``settings.ACCESS_TOKEN_EXPIRE_MINUTES``.

    Returns:
        str: Encoded JWT string with ``type="access"``.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(timezone.utc)
    # JWT payload: sub (subject), iat (issued-at), exp (expiration), type (token kind)
    to_encode: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        "type": "access",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(subject: str) -> str:
    """Create a signed JWT refresh token.

    Refresh tokens have a longer lifetime than access tokens and are
    used only to obtain new access tokens.

    Args:
        subject: The token subject, typically the user ID.

    Returns:
        str: Encoded JWT string with ``type="refresh"``.
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    now = datetime.now(timezone.utc)
    to_encode: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token.

    Args:
        token: The encoded JWT string.

    Returns:
        dict[str, Any]: The decoded payload (contains ``sub``, ``iat``,
            ``exp``, ``type``).

    Raises:
        ValueError: If the token is invalid, expired, or has been tampered with.
    """
    try:
        # Decode verifies the signature and checks the exp claim automatically
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise ValueError("Invalid token")

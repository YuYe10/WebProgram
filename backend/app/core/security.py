"""Security utilities for password hashing and JWT token management. 密码哈希和JWT令牌管理的安全工具

Uses bcrypt for password hashing and python-jose (HS256) for
JSON Web Token creation and validation.

使用bcrypt进行密码哈希，使用python-jose（HS256）进行JSON Web令牌创建和验证。
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash.

    验证明文密码与bcrypt哈希是否匹配。

    Args:
        plain_password: The password provided by the user. 用户提供的密码
        hashed_password: The stored bcrypt hash (as a string). 存储的bcrypt哈希值

    Returns:
        bool: True if the password matches the hash, False otherwise.
              如果密码匹配哈希值返回True，否则返回False
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    使用bcrypt哈希明文密码。

    Args:
        password: The plaintext password to hash. 要哈希的明文密码

    Returns:
        str: The bcrypt hash as a UTF-8 decoded string. UTF-8解码的bcrypt哈希字符串
    """
    # rounds=12 provides a good balance of security and performance
    # rounds=12 在安全性和性能之间提供了良好的平衡
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt(rounds=12)
    ).decode("utf-8")


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token.

    创建已签名的JWT访问令牌。

    Args:
        subject: The token subject, typically the user ID. 令牌主题，通常是用户ID
        expires_delta: Custom expiration duration. Defaults to
            ``settings.ACCESS_TOKEN_EXPIRE_MINUTES``.
            自定义过期时间。默认为settings.ACCESS_TOKEN_EXPIRE_MINUTES

    Returns:
        str: Encoded JWT string with ``type="access"``.
             带有type="access"的编码JWT字符串
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(timezone.utc)
    # JWT payload: sub (subject), iat (issued-at), exp (expiration), type (token kind)
    # JWT载荷：sub（主题）、iat（签发时间）、exp（过期时间）、type（令牌类型）
    to_encode: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        "type": "access",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(subject: str) -> str:
    """Create a signed JWT refresh token.

    创建已签名的JWT刷新令牌。

    Refresh tokens have a longer lifetime than access tokens and are
    used only to obtain new access tokens.

    刷新令牌比访问令牌有效期更长，仅用于获取新的访问令牌。

    Args:
        subject: The token subject, typically the user ID. 令牌主题，通常是用户ID

    Returns:
        str: Encoded JWT string with ``type="refresh"``.
             带有type="refresh"的编码JWT字符串
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

    解码并验证JWT令牌。

    Args:
        token: The encoded JWT string. 编码的JWT字符串

    Returns:
        dict[str, Any]: The decoded payload (contains ``sub``, ``iat``,
            ``exp``, ``type``).
            解码后的载荷（包含sub、iat、exp、type）

    Raises:
        ValueError: If the token is invalid, expired, or has been tampered with.
                    如果令牌无效、过期或被篡改
    """
    try:
        # Decode verifies the signature and checks the exp claim automatically
        # 解码会自动验证签名并检查exp声明
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise ValueError("Invalid token")
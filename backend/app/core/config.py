"""Application configuration.

Loads environment-specific settings from ``.env`` files and system
environment variables using pydantic-settings. All configurable values
are centralised here so the rest of the codebase imports ``settings``
instead of reading env vars directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Values are resolved in this order (later overrides earlier):
    1. Field defaults defined below.
    2. ``.env`` file in the project root.
    3. System environment variables.

    Attributes:
        APP_NAME: Display name of the application.
        DEBUG: Enable debug mode (verbose SQL logging, etc.).
        DATABASE_URL: Async PostgreSQL connection string.
        SECRET_KEY: HMAC secret for JWT signing. **Must be changed in production.**
        ACCESS_TOKEN_EXPIRE_MINUTES: Lifetime of an access token in minutes.
        REFRESH_TOKEN_EXPIRE_DAYS: Lifetime of a refresh token in days.
        CORS_ORIGINS: List of allowed origins for Cross-Origin Resource Sharing.
    """

    # Application
    APP_NAME: str = "Noteworthy API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://noteworthy:noteworthy_secret@localhost:5432/noteworthy"

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Module-level singleton — import this wherever settings are needed
settings = Settings()

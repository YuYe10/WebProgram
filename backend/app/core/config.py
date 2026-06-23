"""Application configuration. 应用配置

Loads environment-specific settings from ``.env`` files and system
environment variables using pydantic-settings. All configurable values
are centralised here so the rest of the codebase imports ``settings``
instead of reading env vars directly.

从 .env 文件和系统环境变量加载环境特定的配置。所有可配置值集中在此，
以便代码库的其他部分导入 settings 而非直接读取环境变量。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables. 应用设置

    Values are resolved in this order (later overrides earlier):
    1. Field defaults defined below.
    2. ``.env`` file in the project root.
    3. System environment variables.

    值按以下顺序解析（后面覆盖前面）：
    1. 下面定义的字段默认值
    2. 项目根目录的 .env 文件
    3. 系统环境变量

    Attributes:
        APP_NAME: Display name of the application. 应用显示名称
        DEBUG: Enable debug mode (verbose SQL logging, etc.). 启用调试模式
        DATABASE_URL: Async PostgreSQL connection string. PostgreSQL异步连接字符串
        SECRET_KEY: HMAC secret for JWT signing. **Must be changed in production.** JWT签名密钥
        ACCESS_TOKEN_EXPIRE_MINUTES: Lifetime of an access token in minutes. Access令牌有效期（分钟）
        REFRESH_TOKEN_EXPIRE_DAYS: Lifetime of a refresh token in days. Refresh令牌有效期（天）
        CORS_ORIGINS: List of allowed origins for Cross-Origin Resource Sharing. 允许的CORS来源列表
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
# 模块级单例 - 需要设置的地方都导入这个
settings = Settings()
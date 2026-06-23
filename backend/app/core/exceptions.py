"""Custom application exceptions and global error handlers. 自定义应用异常和全局错误处理器

Defines a hierarchy of domain-specific exceptions that are automatically
converted to JSON error responses by the registered FastAPI exception
handlers.

定义特定领域的异常层次结构，这些异常由注册的FastAPI异常处理器自动转换为JSON错误响应。
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception. 应用基础异常

    All custom exceptions inherit from this class so that a single
    FastAPI exception handler can catch and format them consistently.

    所有自定义异常都继承此类，以便单个FastAPI异常处理器可以一致地捕获和格式化它们。

    Attributes:
        message: Human-readable error description. 人类可读的错误描述
        status_code: HTTP status code to return. 要返回的HTTP状态码
    """

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


class NotFoundException(AppException):
    """Raised when a requested resource does not exist.

    当请求的资源不存在时引发。

    Returns HTTP 404. 返回HTTP 404
    """

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class UnauthorizedException(AppException):
    """Raised when authentication fails or is missing.

    当身份验证失败或缺失时引发。

    Returns HTTP 401. 返回HTTP 401
    """

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenException(AppException):
    """Raised when the authenticated user lacks permission.

    当已认证用户缺少权限时引发。

    Returns HTTP 403. 返回HTTP 403
    """

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class ConflictException(AppException):
    """Raised when a create operation violates a uniqueness constraint.

    当创建操作违反唯一性约束时引发。

    Returns HTTP 409. 返回HTTP 409
    """

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application.

    在FastAPI应用上注册全局异常处理器。

    Converts ``AppException`` and ``ValueError`` instances into
    structured JSON responses so that route handlers can raise
    exceptions instead of returning ``JSONResponse`` manually.

    将 AppException 和 ValueError 实例转换为结构化的JSON响应，
    以便路由处理器可以引发异常而不是手动返回 JSONResponse。

    Args:
        app: The FastAPI application instance. FastAPI应用实例
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle AppException by returning a JSON error response.

        通过返回JSON错误响应来处理AppException。
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError by returning a 400 JSON error response.

        通过返回400 JSON错误响应来处理ValueError。
        """
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
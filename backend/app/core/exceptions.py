"""Custom application exceptions and global error handlers.

Defines a hierarchy of domain-specific exceptions that are automatically
converted to JSON error responses by the registered FastAPI exception
handlers.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception.

    All custom exceptions inherit from this class so that a single
    FastAPI exception handler can catch and format them consistently.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code to return.
    """

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


class NotFoundException(AppException):
    """Raised when a requested resource does not exist.

    Returns HTTP 404.
    """

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class UnauthorizedException(AppException):
    """Raised when authentication fails or is missing.

    Returns HTTP 401.
    """

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenException(AppException):
    """Raised when the authenticated user lacks permission.

    Returns HTTP 403.
    """

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class ConflictException(AppException):
    """Raised when a create operation violates a uniqueness constraint.

    Returns HTTP 409.
    """

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application.

    Converts ``AppException`` and ``ValueError`` instances into
    structured JSON responses so that route handlers can raise
    exceptions instead of returning ``JSONResponse`` manually.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle AppException by returning a JSON error response."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError by returning a 400 JSON error response."""
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

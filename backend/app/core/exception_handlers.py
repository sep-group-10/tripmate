import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import ApiError, ErrorCode

# Maps a raw HTTP status code to the closest matching error code, for
# framework-raised HTTPExceptions that didn't go through ApiError.
_STATUS_TO_CODE = {
    401: ErrorCode.UNAUTHORIZED,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.NOT_FOUND,
}


def _fallback_code_for_status(status_code: int) -> ErrorCode:
    """Best-effort error code for a status not explicitly mapped above.
    Bucketed by status class so an unmapped 4xx (e.g. 405 Method Not
    Allowed) is never reported as an INTERNAL_SERVER_ERROR - that code
    must only ever mean a real 5xx failure."""
    if status_code in _STATUS_TO_CODE:
        return _STATUS_TO_CODE[status_code]
    if 400 <= status_code < 500:
        return ErrorCode.VALIDATION_ERROR
    return ErrorCode.INTERNAL_SERVER_ERROR


logger = logging.getLogger(__name__)


def _error_body(
    code: ErrorCode, message: str, details: list[dict] | None = None
) -> dict:
    """Build the standard {success: false, error: {...}} response body."""
    error: dict = {"code": code.value, "message": message}
    if details is not None:
        error["details"] = details
    return {"success": False, "error": error}


def register_exception_handlers(app: FastAPI) -> None:
    """Registers one handler per exception type so every error response -
    expected ApiErrors, FastAPI validation errors, raw HTTP errors, and
    anything unhandled - comes back in the same {success, error} shape
    instead of a framework default."""

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError):
        """Handles errors we raised ourselves via ApiError."""
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """Handles request body/query validation failures from Pydantic,
        converting FastAPI's default error list into the field/message
        details format used by VALIDATION_ERROR."""
        details = [
            {
                "field": ".".join(str(loc) for loc in error["loc"] if loc != "body"),
                "message": error["msg"],
            }
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error_body(
                ErrorCode.VALIDATION_ERROR, "Some fields are invalid", details
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handles raw framework HTTP errors (e.g. 404 for an unknown
        route, 405 for a wrong HTTP method) that never went through
        ApiError."""
        code = _fallback_code_for_status(exc.status_code)
        message = (
            exc.detail
            if isinstance(exc.detail, str)
            else "An unexpected error occurred"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(code, message),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Last-resort handler for anything unexpected. The full
        traceback goes to server logs only; the client always gets the
        generic message so internals never leak in a response."""
        logger.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(
                ErrorCode.INTERNAL_SERVER_ERROR, "An unexpected error occurred"
            ),
        )

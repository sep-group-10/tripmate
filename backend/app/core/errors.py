from enum import StrEnum


class ErrorCode(StrEnum):
    """Fixed set of API error codes, per docs/api-contract.md.
    Clients should branch on these values, never on the message text."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED"
    INVALID_REFRESH_TOKEN = "INVALID_REFRESH_TOKEN"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    EXTERNAL_SERVICE_UNAVAILABLE = "EXTERNAL_SERVICE_UNAVAILABLE"


# Maps each error code to the HTTP status it must always be returned with.
ERROR_STATUS_CODES: dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.TOKEN_EXPIRED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.EMAIL_ALREADY_EXISTS: 409,
    ErrorCode.INVALID_CREDENTIALS: 401,
    ErrorCode.ACCOUNT_DEACTIVATED: 403,
    ErrorCode.INVALID_REFRESH_TOKEN: 401,
    ErrorCode.INTERNAL_SERVER_ERROR: 500,
    ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE: 503,
}


class ApiError(Exception):
    """Raise this from route or business logic instead of HTTPException.
    The global handler in exception_handlers.py catches it and converts
    it into the standard {success, error} response shape."""

    def __init__(
        self, code: ErrorCode, message: str, details: list[dict] | None = None
    ):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = ERROR_STATUS_CODES[code]
        super().__init__(message)

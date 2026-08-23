from enum import StrEnum


class ErrorCode(StrEnum):
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
    def __init__(
        self, code: ErrorCode, message: str, details: list[dict] | None = None
    ):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = ERROR_STATUS_CODES[code]
        super().__init__(message)

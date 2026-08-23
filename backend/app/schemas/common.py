from datetime import datetime
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, PlainSerializer

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard success envelope used by every endpoint, per
    docs/api-contract.md: {"success": true, "data": {...}}."""

    success: bool = True
    data: T


# Reusable annotated type for datetime fields so timestamps always
# serialize in the exact ISO 8601 + "Z" format required by the API
# contract (Pydantic's default omits the "Z" suffix).
UTCTimestamp = Annotated[
    datetime,
    PlainSerializer(
        lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%SZ"), return_type=str, when_used="json"
    ),
]

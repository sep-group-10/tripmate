from datetime import datetime
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, PlainSerializer

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T


UTCTimestamp = Annotated[
    datetime,
    PlainSerializer(
        lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%SZ"), return_type=str, when_used="json"
    ),
]

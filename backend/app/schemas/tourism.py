import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DestinationCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    country: str = Field(..., max_length=100)
    region: str | None = Field(default=None, max_length=100)
    latitude: Decimal
    longitude: Decimal
    rating: Decimal | None = Field(default=None, ge=0, le=5)


class DestinationUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    country: str | None = Field(default=None, max_length=100)
    region: str | None = Field(default=None, max_length=100)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=5)


class DestinationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    country: str
    region: str | None
    latitude: Decimal
    longitude: Decimal
    rating: Decimal | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DestinationListData(BaseModel):
    items: list[DestinationResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class DestinationListResponse(BaseModel):
    success: bool = True
    data: DestinationListData
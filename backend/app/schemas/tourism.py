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


class AttractionCreate(BaseModel):
    destination_id: uuid.UUID
    name: str = Field(..., max_length=255)
    description: str | None = None
    latitude: Decimal
    longitude: Decimal
    photo_urls: list[str] | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    opening_hours: dict | None = None
    entry_fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    duration_hours: Decimal | None = Field(default=None, ge=0)


class AttractionUpdate(BaseModel):
    destination_id: uuid.UUID | None = None
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    photo_urls: list[str] | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    opening_hours: dict | None = None
    entry_fee: Decimal | None = Field(default=None, ge=0)
    duration_hours: Decimal | None = Field(default=None, ge=0)


class AttractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    destination_id: uuid.UUID
    name: str
    description: str | None
    latitude: Decimal
    longitude: Decimal
    photo_urls: list[str] | None
    rating: Decimal | None
    opening_hours: dict | None
    entry_fee: Decimal
    duration_hours: Decimal | None
    is_active: bool


class HotelCreate(BaseModel):
    destination_id: uuid.UUID
    name: str = Field(..., max_length=255)
    description: str | None = None
    latitude: Decimal
    longitude: Decimal
    price_per_night: Decimal = Field(..., ge=0)
    facilities: list[str] | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    photo_urls: list[str] | None = None


class HotelUpdate(BaseModel):
    destination_id: uuid.UUID | None = None
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    price_per_night: Decimal | None = Field(default=None, ge=0)
    facilities: list[str] | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    photo_urls: list[str] | None = None


class HotelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    destination_id: uuid.UUID
    name: str
    description: str | None
    latitude: Decimal
    longitude: Decimal
    price_per_night: Decimal
    facilities: list[str] | None
    rating: Decimal | None
    photo_urls: list[str] | None
    is_active: bool

class RestaurantCreate(BaseModel):
    destination_id: uuid.UUID
    name: str = Field(..., max_length=255)
    description: str | None = None
    latitude: Decimal
    longitude: Decimal
    photo_urls: list[str] | None = None
    operating_hours: dict | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    cuisine_type: str = Field(..., max_length=100)
    avg_meal_cost: Decimal = Field(..., ge=0)


class RestaurantUpdate(BaseModel):
    destination_id: uuid.UUID | None = None
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    photo_urls: list[str] | None = None
    operating_hours: dict | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    cuisine_type: str | None = Field(default=None, max_length=100)
    avg_meal_cost: Decimal | None = Field(default=None, ge=0)


class RestaurantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    destination_id: uuid.UUID
    name: str
    description: str | None
    latitude: Decimal
    longitude: Decimal
    photo_urls: list[str] | None
    operating_hours: dict | None
    rating: Decimal | None
    cuisine_type: str
    avg_meal_cost: Decimal
    is_active: bool


class LocalEventCreate(BaseModel):
    destination_id: uuid.UUID
    name: str = Field(..., max_length=255)
    description: str | None = None
    latitude: Decimal
    longitude: Decimal
    photo_urls: list[str] | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    opening_hours: dict | None = None
    duration_hours: Decimal | None = Field(default=None, ge=0)
    entry_fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    event_schedule: dict


class LocalEventUpdate(BaseModel):
    destination_id: uuid.UUID | None = None
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    photo_urls: list[str] | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    opening_hours: dict | None = None
    duration_hours: Decimal | None = Field(default=None, ge=0)
    entry_fee: Decimal | None = Field(default=None, ge=0)
    event_schedule: dict | None = None


class LocalEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    destination_id: uuid.UUID
    name: str
    description: str | None
    latitude: Decimal
    longitude: Decimal
    photo_urls: list[str] | None
    rating: Decimal | None
    opening_hours: dict | None
    duration_hours: Decimal | None
    entry_fee: Decimal
    event_schedule: dict
    is_active: bool
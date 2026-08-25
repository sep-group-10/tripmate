from pydantic import BaseModel, Field


class TripPreferences(BaseModel):
    destination: str | None = None
    dates: str | None = None
    budget: str | None = None
    travelers: int | None = None
    interests: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)

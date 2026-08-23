from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    preferred_travel_style: str | None = Field(default=None, max_length=100)
    preferred_accommodation: str | None = Field(default=None, max_length=100)
    typical_budget_range: str | None = Field(default=None, max_length=100)
    interests: list[str] | None = None

    @field_validator("full_name")
    @classmethod
    def full_name_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Full name cannot be blank or only whitespace")
        return value

    def applied_fields(self) -> dict:
        return self.model_dump(exclude_unset=True)

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProfileUpdateRequest(BaseModel):
    """Request body for PUT /users/me. Only lists fields a user is
    allowed to edit themselves - role, email, and account status are
    deliberately absent, and extra="forbid" rejects any attempt to
    send them instead of silently ignoring it."""

    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    preferred_travel_style: str | None = Field(default=None, max_length=100)
    preferred_accommodation: str | None = Field(default=None, max_length=100)
    typical_budget_range: str | None = Field(default=None, max_length=100)
    interests: list[str] | None = None

    @field_validator("full_name")
    @classmethod
    def full_name_not_blank(cls, value: str | None) -> str | None:
        """Reject a full_name that is present but empty/whitespace-only."""
        if value is not None and not value.strip():
            raise ValueError("Full name cannot be blank or only whitespace")
        return value

    def applied_fields(self) -> dict:
        """Return only the fields the client actually sent, so a
        partial update doesn't overwrite untouched fields with None."""
        return self.model_dump(exclude_unset=True)

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    """Natural-language message sent to a planning session."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        """Reject messages that contain only whitespace."""
        if not value.strip():
            raise ValueError("Message cannot be blank or only whitespace")
        return value


class PlanningSessionInfo(BaseModel):
    """Planning-session details returned with a chat response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    iteration_count: int
    progress_message: str | None
    progress_percentage: int


class ChatResponse(BaseModel):
    """Placeholder assistant reply for a planning session."""

    assistant_message: str
    session: PlanningSessionInfo

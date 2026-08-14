import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.base import Base


class AgentExecutionTrace(Base):
    __tablename__ = "agent_execution_traces"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    planning_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("planning_sessions.id"),
        nullable=False,
    )

    tool_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    tool_input: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    tool_output: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    iteration_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
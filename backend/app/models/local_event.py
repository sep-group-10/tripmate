import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.base import Base


class LocalEvent(Base):
    __tablename__ = "local_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("destinations.id"),
        nullable=False,
    )

    event_schedule: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )
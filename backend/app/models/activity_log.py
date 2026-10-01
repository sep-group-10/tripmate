import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class ActivityLog(Base):
    """One row per notable admin-visible event (entity created/updated/
    deleted, user registered, feedback resolved, ...), for the dashboard's
    Recent Activity feed. Write-only from the app's perspective - rows are
    never updated, only inserted and read."""

    __tablename__ = "activity_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Short category shown as the feed's badge, e.g. "Destination",
    # "Hotel", "User", "Feedback". Free-form on purpose - this is display
    # text, not a foreign key or enum other code branches on.
    kind: Mapped[str] = mapped_column(String(30), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    meta: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

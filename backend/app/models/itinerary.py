import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Itinerary(Base):
    __tablename__ = "itineraries"
    __table_args__ = (
        UniqueConstraint(
            "trip_id", "revision_number", name="uq_itineraries_trip_revision_number"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id"),
        nullable=False,
    )

    # NULL is retained for legacy rows whose historical ordering is unknown.
    revision_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    total_estimated_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    route_info: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    weather_info: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    share_token: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )

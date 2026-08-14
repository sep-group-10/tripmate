import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.base import Base


class Itinerary(Base):
    __tablename__ = "itineraries"

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
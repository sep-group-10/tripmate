import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.base import Base


class Attraction(Base):
    __tablename__ = "attractions"

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
    name: Mapped[str] = mapped_column(
    String(255),
    nullable=False,
)

    description: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
)

    rating: Mapped[Decimal | None] = mapped_column(
    Numeric(2, 1),
    nullable=True,
)

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    opening_hours: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    entry_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    duration_hours: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )
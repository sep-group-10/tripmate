import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.base import Base


class Hotel(Base):
    __tablename__ = "hotels"

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

    price_per_night: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    facilities: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )

    rating: Mapped[Decimal | None] = mapped_column(
        Numeric(2, 1),
        nullable=True,
    )

    photo_urls: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
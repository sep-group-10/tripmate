import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.base import Base


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
    )

    travel_start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    travel_end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    budget: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    travel_style: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    accommodation_preference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
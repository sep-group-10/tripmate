import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.base import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

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

    cuisine_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    avg_meal_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
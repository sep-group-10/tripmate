import uuid
from decimal import Decimal

from sqlalchemy import Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class TransportRate(Base):
    __tablename__ = "transport_rates"

    __table_args__ = (
        UniqueConstraint(
            "transport_type",
            "region",
            name="uq_transport_rates_type_region",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    transport_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    region: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    cost_per_km: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    base_fare: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

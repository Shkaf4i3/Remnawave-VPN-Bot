from datetime import datetime, timezone
from enum import Enum as enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Enum, func, Numeric, ForeignKey

from .base import Base


class PaymentStatus(str, enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class Payment(Base):
    __tablename__ = "Payment"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        unique=True,
        server_default=func.uuidv7(),
    )
    tg_id: Mapped[int] = mapped_column(ForeignKey(column="User.tg_id"), nullable=False)
    invoice_id: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(precision=10, scale=5), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
    )

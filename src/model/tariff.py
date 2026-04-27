from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, func, Numeric

from .base import Base


class Tariff(Base):
    __tablename__ = "Tariff"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        unique=True,
        server_default=func.uuidv7(),
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(
        Numeric(precision=10, scale=5, asdecimal=False),
        nullable=False,
    )
    device_limit: Mapped[int] = mapped_column(Integer, default=1)
    remnawave_squad_id: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
    )

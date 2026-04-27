from datetime import datetime, timezone
from enum import Enum as enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Enum, func, ForeignKey, BigInteger, TypeDecorator, UUID
from cryptography.fernet import Fernet

from .base import Base
from ..core import settings


fernet = Fernet(key=settings.fernet_key)


class EncryptedString(TypeDecorator):
    impl = String
    cache_ok = True


    def process_bind_param(self, value, dialect) -> str | None:
        if value is None:
            return value
        return fernet.encrypt(data=value.encode()).decode()

    def process_result_value(self, value, dialect) -> str | None:
        if value is None:
            return value
        return fernet.decrypt(token=value.encode()).decode()


class SubscriptionStatus(str, enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Subscription(Base):
    __tablename__ = "Subscription"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        unique=True,
        server_default=func.uuidv7(),
    )
    user_id: Mapped[str] = mapped_column(ForeignKey(column="User.id"), nullable=False)
    tariff_id: Mapped[str] = mapped_column(ForeignKey(column="Tariff.id"), nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus),
        default=SubscriptionStatus.ACTIVE,
    )
    remnawave_user_uuid: Mapped[UUID | None] = mapped_column(UUID, nullable=True)
    remnawave_short_uuid: Mapped[str | None] = mapped_column(String, nullable=True)
    config_url: Mapped[str | None] = mapped_column(EncryptedString(255), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
    )

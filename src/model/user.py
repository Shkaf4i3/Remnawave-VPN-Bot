from datetime import datetime, timezone
from enum import Enum as enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, BigInteger, Enum, func, Numeric, Boolean, ForeignKey

from .base import Base


class Role(enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "User"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        unique=True,
        server_default=func.uuidv7(),
    )
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    is_blocked: Mapped[bool | None] = mapped_column(Boolean, default=False)
    balance: Mapped[float] = mapped_column(
        Numeric(precision=10, scale=5, asdecimal=False),
        nullable=False,
        default=0,
    )
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False, default=Role.USER)
    referred_by_id: Mapped[str | None] = mapped_column(
        ForeignKey(column="User.id"),
        nullable=True,
        index=True,
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

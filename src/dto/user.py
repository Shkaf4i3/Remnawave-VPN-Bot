from datetime import datetime

from pydantic import BaseModel

from ..model import Role


class UserDto(BaseModel):
    id: str
    tg_id: int
    balance: float
    role: Role
    created_at: datetime
    is_blocked: bool | None = None
    updated_at: datetime | None = None
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    referred_by_id: str | None = None

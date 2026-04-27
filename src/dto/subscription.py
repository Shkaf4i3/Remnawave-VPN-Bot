from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from ..model import SubscriptionStatus


class SubscriptionDto(BaseModel):
    id: str
    user_id: str
    tariff_id: str
    status: SubscriptionStatus
    expires_at: datetime
    created_at: datetime
    remnawave_user_uuid: UUID | None = None
    remnawave_short_uuid: str | None = None
    config_url: str | None = None
    updated_at: datetime | None = None

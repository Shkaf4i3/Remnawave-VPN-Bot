from datetime import datetime

from pydantic import BaseModel


class TariffDto(BaseModel):
    id: str
    name: str
    duration_days: int
    price: float
    device_limit: int
    created_at: datetime
    description: str | None = None
    remnawave_squad_id: str | None = None
    updated_at: datetime | None = None

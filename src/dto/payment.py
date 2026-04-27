from datetime import datetime

from pydantic import BaseModel

from ..model import PaymentStatus


class PaymentDto(BaseModel):
    id: str
    tg_id: int
    invoice_id: str
    amount: float
    status: PaymentStatus
    created_at: datetime

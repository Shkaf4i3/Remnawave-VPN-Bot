from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field, field_validator


class InvoicePaidPayloadDto(BaseModel):
    invoice_id: int
    hash: str
    currency_type: Literal["fiat", "crypto"] = Field(..., alias="currency_type")
    fiat: str
    amount: float
    paid_asset: str
    paid_amount: float
    paid_fiat_rate: float
    accepted_assets: List[str]
    fee_asset: str
    fee_amount: float
    fee: float
    fee_in_usd: float
    pay_url: str
    bot_invoice_url: str
    mini_app_invoice_url: str
    web_app_invoice_url: str
    status: Literal["active", "paid", "expired"]
    created_at: datetime
    allow_comments: bool
    allow_anonymous: bool
    expiration_date: datetime
    paid_usd_rate: float
    usd_rate: float
    paid_at: datetime
    paid_anonymously: bool

    @field_validator("created_at", "expiration_date", "paid_at", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | datetime) -> datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value


class CryptoBotWebhookDto(BaseModel):
    update_id: int
    update_type: Literal["invoice_paid"]
    request_date: datetime
    payload: InvoicePaidPayloadDto

    @field_validator("request_date", mode="before")
    @classmethod
    def parse_request_date(cls, value: str | datetime) -> datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

from datetime import datetime

from pydantic import BaseModel, field_validator


class LolzteamWebhookDto(BaseModel):
    additional_data: str = ""
    amount: float
    callback_date: int = 0
    comment: str
    expires_at: int
    invoice_date: int
    invoice_id: int
    is_test: bool
    merchant_id: int
    paid_date: int
    payer_user_id: int
    payment_id: str
    required_telegram_id: int
    required_telegram_username: str
    resend_attempts: int
    status: str
    url: str
    url_callback: str
    url_success: str
    user_id: int

    @property
    def expires_at_dt(self) -> datetime:
        return datetime.fromtimestamp(self.expires_at)

    @property
    def invoice_date_dt(self) -> datetime:
        return datetime.fromtimestamp(self.invoice_date)

    @property
    def paid_date_dt(self) -> datetime | None:
        return datetime.fromtimestamp(self.paid_date) if self.paid_date else None
    @field_validator("amount", mode="before")
    @classmethod
    def parse_amount(cls, value: str | float) -> float:
        if isinstance(value, str):
            return float(value)
        return value

    @field_validator("callback_date", "expires_at", "invoice_date", "paid_date",
                     "invoice_id", "merchant_id", "payer_user_id", "resend_attempts",
                     "required_telegram_id", "user_id", mode="before")
    @classmethod
    def parse_int_fields(cls, value: str | int) -> int:
        if isinstance(value, str):
            return int(value)
        return value

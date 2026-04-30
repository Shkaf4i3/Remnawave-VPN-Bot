from pydantic import BaseModel, Field, ConfigDict


class HeleketPaymentWebhookDto(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str
    uuid: str | None = None
    order_id: str | None = None
    amount: str
    payment_amount: str
    payment_amount_usd: str
    merchant_amount: str
    commission: str
    is_final: bool
    status: str
    from_: str = Field(alias="from")
    wallet_address_uuid: str | None = None
    network: str
    currency: str
    payer_currency: str
    payer_amount: str
    payer_amount_exchange_rate: str | None = None
    additional_data: str | None = None
    transfer_id: str | None = None
    txid: str
    sign: str

from uuid import uuid4

from HeleketAPI import HeleketClient
from HeleketAPI.types import PaymentInfoResponse

from ..core import settings


class Heleket:
    def __init__(self) -> None:
        self.heleket_client = HeleketClient(
            merchant_id=settings.heleket_merchant_id,
            api_key=settings.heleket_get_invoices_token,
        )

    def _generate_order_id(self) -> str:
        return str(uuid4())


    async def create_invoice(self, amount: float) -> PaymentInfoResponse:
        order_id = self._generate_order_id()
        url_success = "https://t.me/zakaztestbots_bot"
        return await self.heleket_client.create_invoice(
            amount=amount,
            currency="USD",
            order_id=order_id,
            url_success=url_success,
            url_callback=settings.heleket_webhook_url,
            lifetime=600,
        )


    async def check_invoice(self, order_id: str, uuid: str) -> PaymentInfoResponse:
        return await self.heleket_client.get_payment_info(
            order_id=order_id,
            uuid=uuid,
        )

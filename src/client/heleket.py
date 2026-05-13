from uuid import uuid4

from HeleketAPI import HeleketClient

from ..core import settings
from .invoice import Invoice


class Heleket:
    def __init__(self) -> None:
        self.heleket_client = HeleketClient(
            merchant_id=settings.heleket_merchant_id,
            api_key=settings.heleket_get_invoices_token,
        )

    def _generate_order_id(self) -> str:
        return str(uuid4())


    async def create_invoice(self, amount: float) -> Invoice:
        order_id = self._generate_order_id()
        url_success = "https://t.me/zakaztestbots_bot"
        invoice = await self.heleket_client.create_invoice(
            amount=amount,
            currency="USD",
            order_id=order_id,
            url_success=url_success,
            url_callback=settings.heleket_webhook_url,
            lifetime=600,
        )
        return Invoice(invoice_id=invoice.order_id, url=invoice.url)

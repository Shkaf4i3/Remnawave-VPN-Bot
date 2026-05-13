from time import time_ns

from AsyncPayments.lolz import AsyncLolzteamMarketPayment

from ..core import settings
from .invoice import Invoice


class LolzTeam:
    def __init__(self) -> None:
        self.lolz_client = AsyncLolzteamMarketPayment(token=settings.lolzteam_token)

    def _generate_payment_id(self) -> int:
        return time_ns()


    async def create_invoice(
        self,
        amount: float,
        required_telegram_id: int,
        required_telegram_username: str,
    ) -> Invoice:
        payment_id = self._generate_payment_id()
        url_success = "https://t.me/zakaztestbots_bot"
        invoice = await self.lolz_client.create_invoice(
            amount=amount,
            payment_id=payment_id,
            comment=f"Create new payment by id {payment_id}",
            url_success=url_success,
            merchant_id=settings.merchant_id,
            currency="rub",
            lifetime=600,
            required_telegram_id=required_telegram_id,
            required_telegram_username=required_telegram_username,
            url_callback=settings.lolz_webhook_url,
        )
        return Invoice(
            invoice_id=str(invoice.invoice_id),
            url=invoice.url,
            payment_id=invoice.payment_id,
        )

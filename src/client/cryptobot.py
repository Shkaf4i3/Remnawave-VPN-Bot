from AsyncPayments.cryptoBot import AsyncCryptoBot

from ..core import settings
from .invoice import Invoice


class CryptoBot:
    def __init__(self) -> None:
        self.crypto_pay = AsyncCryptoBot(token=settings.crypto_bot_token, is_testnet=False)


    async def create_invoice(self, amount: float) -> Invoice:
        invoice = await self.crypto_pay.create_invoice(
            amount=amount,
            currency_type="fiat",
            asset="USDT",
            fiat="RUB",
        )
        return Invoice(invoice_id=str(invoice.invoice_id), url=invoice.bot_invoice_url)


    async def delete_invoice(self, invoice_id: int) -> bool:
        return await self.crypto_pay.delete_invoice(invoice_id=invoice_id)

from AsyncPayments.cryptoBot import AsyncCryptoBot
from AsyncPayments.cryptoBot.api import Invoice as CryptoInvoice

from ..core import settings


class CryptoBot:
    def __init__(self) -> None:
        self.crypto_pay = AsyncCryptoBot(token=settings.crypto_bot_token, is_testnet=False)


    async def create_invoice(self, amount: float) -> CryptoInvoice:
        return await self.crypto_pay.create_invoice(
            amount=amount,
            currency_type="fiat",
            asset="USDT",
            fiat="RUB",
        )


    async def delete_invoice(self, invoice_id: int) -> bool:
        return await self.crypto_pay.delete_invoice(invoice_id=invoice_id)


    async def check_invoice(self, invoice_id: int) -> CryptoInvoice:
        return await self.crypto_pay.get_invoices(
            invoice_ids=invoice_id,
            count=1,
        )

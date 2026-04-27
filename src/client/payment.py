from typing import Literal

from AsyncPayments.cryptoBot.api import Invoice as CryptoInvoice
from AsyncPayments.lolz.api import Invoice as LolzInvoice

from .cryptobot import CryptoBot
from .lolzteam import LolzTeam


class PaymentSystem:
    def __init__(self, crypto_bot: CryptoBot, lolz_client: LolzTeam) -> None:
        self.crypto_bot = crypto_bot
        self.lolz_client = lolz_client


    async def create_invoice(
        self,
        type_client: Literal["lolz", "cryptobot"],
        amount: float,
        required_telegram_id: int | None = None,
        required_telegram_username: str | None = None,
    ) -> CryptoInvoice | LolzInvoice:
        if type_client == "lolz":
            return await self.lolz_client.create_invoice(
                amount=amount,
                required_telegram_id=required_telegram_id,
                required_telegram_username=required_telegram_username,
            )
        elif type_client == "cryptobot":
            return await self.crypto_bot.create_invoice(amount=amount)


    async def check_invoice(
        self,
        type_client: Literal["lolz", "cryptobot"],
        invoice_id: str | int,
        payment_id: str | None = None,
    ) -> CryptoInvoice | LolzInvoice:
        if type_client == "lolz":
            return await self.lolz_client.check_invoice(
                invoice_id=invoice_id,
                payment_id=payment_id,
            )
        elif type_client == "cryptobot":
            return await self.crypto_bot.check_invoice(invoice_id=invoice_id)


    async def delete_invoice(self, invoice_id: int) -> bool:
        """Available only for cryptobot payment"""
        return await self.crypto_bot.delete_invoice(invoice_id=invoice_id)

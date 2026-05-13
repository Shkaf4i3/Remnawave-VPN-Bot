from typing import Literal

from .cryptobot import CryptoBot
from .lolzteam import LolzTeam
from .heleket import Heleket
from .invoice import Invoice


class PaymentSystem:
    def __init__(
        self,
        crypto_bot: CryptoBot,
        lolz_client: LolzTeam,
        heleket_client: Heleket,
    ) -> None:
        self.crypto_bot = crypto_bot
        self.lolz_client = lolz_client
        self.heleket_client = heleket_client


    async def create_invoice(
        self,
        type_client: Literal["lolz", "cryptobot", "heleket"],
        amount: float,
        required_telegram_id: int | None = None,
        required_telegram_username: str | None = None,
    ) -> Invoice:
        if type_client == "lolz":
            return await self.lolz_client.create_invoice(
                amount=amount,
                required_telegram_id=required_telegram_id,
                required_telegram_username=required_telegram_username,
            )
        elif type_client == "cryptobot":
            return await self.crypto_bot.create_invoice(amount=amount)
        elif type_client == "heleket":
            return await self.heleket_client.create_invoice(amount=amount)


    async def delete_invoice(self, invoice_id: int) -> bool:
        """Available only for cryptobot payment"""
        return await self.crypto_bot.delete_invoice(invoice_id=invoice_id)

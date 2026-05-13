from typing import Any, Dict, Literal
from logging import getLogger

from aiogram.types import Update
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import StorageKey
from fastapi import HTTPException, status

from .payment import PaymentService
from .user import UserService
from .tariff import TariffService
from .subscription import SubscriptionService
from .analytics import AnalyticsService
from .cache import CacheService
from ..core import settings
from ..app import bot, dp
from ..dto import CryptoBotWebhookDto, LolzteamWebhookDto, HeleketPaymentWebhookDto
from ..model import PaymentStatus
from ..aiogram_functions import kb
from ..client import PaymentSystem


logger = getLogger(name=__name__)


class WebhookService:
    def __init__(
        self,
        user_service: UserService,
        payment_service: PaymentService,
        tariff_service: TariffService,
        subscription_service: SubscriptionService,
        analytics_service: AnalyticsService,
        cache_service: CacheService,
        payment_system: PaymentSystem,
    ) -> None:
        self.user_service = user_service
        self.payment_service = payment_service
        self.tariff_service = tariff_service
        self.subscription_service = subscription_service
        self.analytics_service = analytics_service
        self.cache_service = cache_service
        self.payment_system = payment_system


    async def _get_usd_to_rub_rate(self) -> float:
        cache_key = "forex:usd_rub"
        backup_key = "forex:usd_rub:last_success"
        cached = await self.cache_service.get_value(key=cache_key)
        if cached:
            return float(cached)
        backup = await self.cache_service.get_value(key=backup_key)
        if backup is not None:
            return float(backup)

    def _get_fsm_storage(self) -> RedisStorage:
        return dp.storage


    async def _handle_webhook(
        self,
        type_update: Literal["lolz", "cryptobot", "heleket"],
        update: Dict[str, Any],
    ) -> None:
        try:
            referrer_user = None
            if type_update == "cryptobot":
                validate_model = CryptoBotWebhookDto.model_validate(
                    obj=update,
                    by_alias=True,
                    by_name=True,
                )
                invoice_id = str(validate_model.payload.invoice_id)
                status = validate_model.payload.status
                amount = validate_model.payload.amount
            elif type_update == "lolz":
                validate_model = LolzteamWebhookDto.model_validate(
                    obj=update,
                    by_alias=True,
                    by_name=True,
                )
                invoice_id = str(validate_model.invoice_id)
                status = validate_model.status
                amount = validate_model.amount
            elif type_update == "heleket":
                validate_model = HeleketPaymentWebhookDto.model_validate(
                    obj=update,
                    by_alias=True,
                    by_name=True,
                )
                invoice_id = validate_model.order_id
                status = validate_model.status
                course = await self._get_usd_to_rub_rate()
                amount = float(validate_model.amount) * course
            existing_payment = await self.payment_service.get_payment_by_invoice_id(
                invoice_id=invoice_id,
            )
            tg_id = existing_payment.tg_id
            exiting_user = await self.user_service.get_user_by_tg_id(tg_id=tg_id)
            if exiting_user and exiting_user.referred_by_id:
                referrer_user = await self.user_service.get_user_by_id(
                    id=exiting_user.referred_by_id,
                )
            storage = self._get_fsm_storage()
            if existing_payment and status == "paid":
                key = StorageKey(chat_id=tg_id, user_id=tg_id, bot_id=bot.id)
                await self.user_service.update_balance_user(
                    tg_id=tg_id,
                    amount=amount,
                    type_update="plus",
                )
                ref_amount = amount * 0.1
                if referrer_user:
                    await self.user_service.update_balance_user(
                        tg_id=referrer_user.tg_id,
                        amount=ref_amount,
                        type_update="plus",
                    )
                await self.payment_service.update_payment_by_invoice_id(
                    invoice_id=invoice_id,
                    status=PaymentStatus.PAID,
                )
                text = "✅ Платеж прошел, ваш баланс пополнен! ✅"
                await bot.send_message(
                    chat_id=tg_id,
                    text=text,
                    reply_markup=kb.menu_kb(),
                )
                await storage.set_state(key=key, state=None)
                await storage.set_data(key=key, data={})
        except Exception as e:
            text = "🆘 Произошла непредвиденная ошибка 🆘. Попробуйте еще раз"
            await bot.send_message(chat_id=tg_id, text=text)
            logger.error("Произошла непредвиденная ошибка - %s", str(e))


    async def handle_tg_webhook_update(
        self,
        update: Dict[str, Any],
        x_telegram_bot_api_secret_token: str,
    ) -> None:
        if x_telegram_bot_api_secret_token != settings.secret_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid secret token",
            )
        new_update = Update.model_validate(obj=update, by_alias=True, by_name=True)
        dp["user_service"] = self.user_service
        dp["payment_service"] = self.payment_service
        dp["tariff_service"] = self.tariff_service
        dp["subscription_service"] = self.subscription_service
        dp["analytics_service"] = self.analytics_service
        dp["payment_system"] = self.payment_system
        await dp.feed_update(bot=bot, update=new_update)


    async def handle_cryptobot_webhook_update(self, update: Dict[str, Any]) -> None:
        await self._handle_webhook(type_update="cryptobot", update=update)


    async def handle_lolzteam_webhook_update(self, update: Dict[str, Any]) -> None:
        await self._handle_webhook(type_update="lolz", update=update)


    async def handle_heleket_webhook_update(self, update: Dict[str, Any]) -> None:
        await self._handle_webhook(type_update="heleket", update=update)

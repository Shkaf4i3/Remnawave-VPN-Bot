from logging import Logger
from typing import Literal

from aiogram.types import Message, CallbackQuery
from remnawave.exceptions import ApiError, BadRequestError, NetworkError, ServerError

from ..service import SubscriptionService, UserService, TariffService
from ..client import RemnawaveClient
from ..model import SubscriptionStatus
from ..aiogram_functions import kb


async def get_profile_subcription(
    update: Message | CallbackQuery,
    user_service: UserService,
    subscription_service: SubscriptionService,
    tariff_service: TariffService,
    remnawave_client: RemnawaveClient,
    logger: Logger,
    type: Literal["open", "back"],
) -> None:
    message = update
    if isinstance(update, CallbackQuery):
        message = update.message
    existing_user = await user_service.get_user_by_tg_id(tg_id=update.from_user.id)
    existing_subscription = await subscription_service.get_subscription_by_user_id(
        user_id=existing_user.id,
    )
    if existing_subscription:
        existing_tariff = await tariff_service.get_tariff_by_tariff_id(
            tariff_id=existing_subscription.tariff_id,
        )
        try:
            device_limit = existing_tariff.device_limit
            subs_devices = await remnawave_client.get_user_active_devices(
                uuid=str(existing_subscription.remnawave_user_uuid),
            )
            status = (
                "Активна ✅"
                if existing_subscription.status == SubscriptionStatus.ACTIVE
                else "Неактивна ❌"
            )
            text = (
                "💼 Меню управления вашей подпиской 💼\n\n"
                f"Статус - {status}\n"
                f"📎 Url подписки - <code>{existing_subscription.config_url}</code> 📎\n"
                f"📅 Подписка активна до - {existing_subscription.expires_at.strftime(format=r"%d/%m/%Y")} 📅\n"
                f"Количество активных пользователей на этой подписке - {len(subs_devices)}/{device_limit} шт.\n\n"
                "<i>Для управления подпиской воспользуйтесь меню ниже</i>"
            )
            if type == "open":
                await message.answer(
                    text=text,
                    reply_markup=kb.manage_subscription(subscription_id=existing_subscription.id),
                )
            elif type == "back":
                await message.edit_text(
                    text=text,
                    reply_markup=kb.manage_subscription(subscription_id=existing_subscription.id),
                )
        except ApiError as e:
            text = "🆘 Произошла ошибка сервиса, попробуйте еще раз 🆘"
            await message.answer(text=text)
            logger.error("Произошла ошибка API - %s", str(e))
        except NetworkError as e:
            text = "🆘 Произошла ошибка сети, попробуйте еще раз 🆘"
            await message.answer(text=text)
            logger.error("Произошла ошибка сети - %s", str(e))
        except BadRequestError as e:
            text = "🆘 Произошла ошибка клиента, попробуйте еще раз 🆘"
            await message.answer(text=text)
            logger.error("Произошла ошибка клиента - %s", str(e))
        except ServerError as e:
            text = "🆘 Произошла ошибка сервера, попробуйте еще раз 🆘"
            await message.answer(text=text)
            logger.error("Произошла ошибка сервера - %s", str(e))
        except Exception as e:
            text = "🆘 Произошла неожиданная ошибка, попробуйте еще раз 🆘"
            await message.answer(text=text)
            logger.error("Произошла неожиданная ошибка - %s", str(e))
    else:
        text = "❌ В данный момент у вас нету активной подписки ❌"
        await message.answer(text=text)

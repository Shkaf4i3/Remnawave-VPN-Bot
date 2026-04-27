from logging import getLogger
from asyncio import sleep

from faststream import Context
from faststream.rabbit import RabbitQueue, RabbitMessage
from aiogram import Bot
from aiogram.exceptions import (
    TelegramRetryAfter,
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramAPIError,
)
from remnawave.enums import UserStatus

from ..client import broker, redis, RemnawaveClient
from ..dto import MailingTaskDto
from .producer import direct_exchange
from ..service import CacheService
from ..repo import SubscriptionRepo, UserRepo
from ..core import db_helper
from ..model import SubscriptionStatus


logger = getLogger(name=__name__)
mailing_queue = RabbitQueue(name="send-mailing", routing_key="tg_id", durable=True)
schedule_queue = RabbitQueue(name="schedule_subs", routing_key="subs_id", durable=True)


@broker.subscriber(queue=schedule_queue, exchange=direct_exchange)
async def sync_subscriptions_task(
    message: RabbitMessage,
    bot: Bot = Context("bot"),
) -> None:
    async with db_helper.session_factory() as session:
        subscription_repo = SubscriptionRepo(session=session)
        user_repo = UserRepo(session=session)
        cache_service = CacheService(redis=redis, default_ttl=300)
        remnawave_client = RemnawaveClient(cache_service=cache_service)
        subscriptions = await subscription_repo.get_active_subscriptions()
        for subscription in subscriptions:
            try:
                if not subscription.remnawave_user_uuid:
                    continue
                try:
                    user_info = await remnawave_client.get_subscription_info_by_short_uuid(
                        short_uuid=subscription.remnawave_short_uuid,
                    )
                except Exception as e:
                    logger.warning(
                        "Ошибка API для подписки %s, повтор позже: %s",
                        subscription.id,
                        str(e),
                    )
                    await message.nack(requeue=True)
                    return
                if user_info.status == UserStatus.EXPIRED:
                    subscription.status = SubscriptionStatus.EXPIRED
                    session.add(instance=subscription)
                    await session.commit()
                    try:
                        user_info = await user_repo.get_user_by_id(id=subscription.user_id)
                        text = (
                            "🆘 У вашей подписки закончился срок работы 🆘\n\n"
                            "✅ Для дальнейшего доступа к ней перейдите в раздел управления подпиской ✅"
                        )
                        await bot.send_message(chat_id=user_info.tg_id, text=text)
                        await sleep(delay=0.2)
                    except TelegramRetryAfter as e:
                        logger.warning(
                            "Flood control для %s, ждем %s",
                            user_info.tg_id,
                            e.retry_after,
                        )
                        await sleep(delay=e.retry_after)
                    except TelegramForbiddenError:
                        logger.info("Пользователь %s заблокировал бота", user_info.tg_id)
                    except TelegramBadRequest as e:
                        logger.error("Невалидный запрос для %s - %s", user_info.tg_id, str(e))
                        await message.reject(requeue=False)
                        return
                    except TelegramAPIError as e:
                        logger.error("Ошибка telegram для %s - %s", user_info.tg_id, str(e))
                        await message.nack(requeue=True)
                        return
            except Exception as e:
                logger.error("Произошла критическая ошибка - %s", str(e))
                await message.nack(requeue=True)
                return
    await message.ack()


@broker.subscriber(queue=mailing_queue, exchange=direct_exchange)
async def handle_mailing_message(
    task: MailingTaskDto,
    message: RabbitMessage,
    bot: Bot = Context("bot"),
) -> None:
    try:
        if task.message_type == "photo":
            await bot.send_photo(
                chat_id=task.tg_id,
                photo=task.message_media,
                caption=task.message_text,
            )
        elif task.message_type == "document":
            await bot.send_document(
                chat_id=task.tg_id,
                document=task.message_media,
                caption=task.message_text,
            )
        elif task.message_type == "text":
            await bot.send_message(
                chat_id=task.tg_id,
                text=task.message_text,
            )
        await message.ack()
    except TelegramRetryAfter as e:
        if task.retry_count > task.MAX_RETRIES:
            await message.nack(requeue=True)
            logger.error("Превышен лимит попыток для пользователя %s", task.tg_id)
            return
        task.retry_count += 1
        logger.warning(
            "Flood control для пользователя %s, повтор через %s сек.",
            task.tg_id,
            e.retry_after,
        )
        await sleep(e.retry_after)
        await message.nack(requeue=True)
    except TelegramForbiddenError:
        await message.ack()
        logger.info("Пользователь %s заблокировал бота, деактивируем.", task.tg_id)
    except TelegramBadRequest as e:
        await message.reject(requeue=False)
        logger.error(
            "Невалидный запрос для пользователя %s: %s",
            task.tg_id,
            str(e),
        )
    except TelegramAPIError as e:
        logger.exception(
            "Ошибка Telegram API при отправке пользователю %s: %s",
            task.tg_id,
            str(e),
        )
    except Exception as e:
        logger.error("Произошла неожиданная ошибка - %s", str(e))

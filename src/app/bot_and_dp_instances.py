from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from ..core import settings


def create_bot() -> Bot:
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML,),
    )
    return bot


def create_dispatcher() -> Dispatcher:
    storage = RedisStorage.from_url(url=settings.redis_url)
    dp = Dispatcher(storage=storage)
    return dp


bot = create_bot()
dp = create_dispatcher()

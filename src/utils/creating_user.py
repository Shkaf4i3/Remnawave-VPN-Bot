from aiogram.types import Message

from ..service import UserService
from ..aiogram_functions import kb


async def create_user(
    message: Message,
    user_service: UserService,
    referrer_user_id: int | None = None
) -> None:
    if referrer_user_id == message.from_user.id:
        referrer_user_id = None
    referrer_user = None
    if referrer_user_id:
        referrer_user = await user_service.get_user_by_tg_id(tg_id=referrer_user_id)
        await user_service.cache_service.delete_key(key=f"users:ref:{referrer_user.tg_id}")
    await user_service.save_user(
        tg_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        referred_by_id=referrer_user.id if referrer_user else None,
    )
    text = (
        f"👋 Привет, {message.from_user.first_name} 👋. Добро пожаловать в CrazyFrootShoop VPN бот!\n"
        "В этом боте ты сможешь приобрести конфигурации VPN на свой вкус 🛒\n"
        "Для взаимодествия с ботом воспользуйся меню ниже 👇"
    )
    await message.answer(text=text, reply_markup=kb.menu_kb())

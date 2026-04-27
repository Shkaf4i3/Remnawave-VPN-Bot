from aiogram.filters import Filter
from aiogram.types import Message

from ..model import Role
from ..service import UserService


class IsAdmin(Filter):
    async def __call__(self, message: Message, user_service: UserService) -> bool:
        existing_user = await user_service.get_user_by_tg_id(tg_id=message.from_user.id)
        return existing_user is not None and existing_user.role == Role.ADMIN

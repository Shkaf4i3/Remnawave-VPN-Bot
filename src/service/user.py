from datetime import datetime, timezone
from typing import Literal

from ..dto import UserDto
from ..model import User, Role
from ..mappings import user_mappings
from ..repo import UnitOfWork, UserRepo, transactional
from ..core import settings
from .cache import CacheService


class UserService:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        user_repo: UserRepo,
        cache_service: CacheService,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.user_repo = user_repo
        self.cache_service = cache_service


    async def _internal_get_count_users_by_tg_id(self, tg_id: int) -> int:
        existing_user = await self.user_repo.get_user_by_tg_id(tg_id=tg_id)
        count_users = await self.user_repo.get_count_user_by_referrer_user_id(
            referrer_user_id=existing_user.id,
        )
        return count_users if count_users else 0


    @transactional
    async def create_admin_on_startup(self) -> None:
        existing_admin_user = await self.user_repo.get_user_by_tg_id(tg_id=settings.admin_ids[0])
        if not existing_admin_user:
            new_admin_user = User(
                tg_id=settings.admin_ids[0],
                role=Role.ADMIN,
            )
            await self.user_repo.save_user(user=new_admin_user)


    @transactional
    async def save_user(
        self,
        tg_id: int,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
        referred_by_id: str | None = None,
    ) -> None:
        exists_user = await self.user_repo.get_user_by_tg_id(tg_id=tg_id)
        if exists_user:
            return None
        new_user = User(
            tg_id=tg_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            referred_by_id=referred_by_id,
        )
        await self.user_repo.save_user(user=new_user)


    async def get_user_by_tg_id(self, tg_id: int) -> UserDto | None:
        exists_user = await self.user_repo.get_user_by_tg_id(tg_id=tg_id)
        if not exists_user:
            return None
        return user_mappings.map_user(user=exists_user)


    async def get_user_by_id(self, id: int) -> UserDto | None:
        exists_user = await self.user_repo.get_user_by_id(id=id)
        if not exists_user:
            return None
        return user_mappings.map_user(user=exists_user)


    async def get_count_users_by_tg_id(self, tg_id: int) -> int:
        cached = await self.cache_service.get_value(key=f"users:ref:{tg_id}")
        if cached is not None:
            return cached
        count_users = await self._internal_get_count_users_by_tg_id(tg_id=tg_id)
        await self.cache_service.set_value(
            key=f"users:ref:{tg_id}",
            value=count_users,
            ttl=600,
        )
        return count_users


    @transactional
    async def update_balance_user(
        self,
        tg_id: int,
        amount: float,
        type_update: Literal["plus", "minus"],
    ) -> None:
        exists_user = await self.user_repo.get_user_by_tg_id(tg_id=tg_id)
        if exists_user:
            if type_update == "plus":
                exists_user.balance += amount
            elif type_update == "minus":
                exists_user.balance -= amount
            exists_user.updated_at = datetime.now(tz=timezone.utc)
            await self.user_repo.save_user(user=exists_user)


    async def get_list_users(self) -> list[UserDto]:
        users = await self.user_repo.get_list_users()
        return [user_mappings.map_user(user=user) for user in users]

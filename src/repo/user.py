from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..model import User


class UserRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def save_user(self, user: User) -> User:
        self.session.add(instance=user)
        await self.session.flush()
        await self.session.refresh(instance=user)
        return user


    async def get_user_by_tg_id(self, tg_id: int) -> User | None:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def get_user_by_id(self, id: int) -> User | None:
        stmt = select(User).where(User.id == id)
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def get_count_user_by_referrer_user_id(self, referrer_user_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(User.referred_by_id == referrer_user_id)

        )
        result = await self.session.execute(statement=stmt)
        return result.scalar_one()


    async def get_list_users(self) -> list[User]:
        stmt = select(User)
        result = await self.session.execute(statement=stmt)
        return result.scalars().unique().all()


    async def get_count_users_since(self, start_date: datetime) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(User.created_at >= start_date)
        )
        result = await self.session.execute(statement=stmt)
        return result.scalar_one()


    async def get_count_users_total(self) -> int:
        stmt = select(func.count()).select_from(User)
        result = await self.session.execute(statement=stmt)
        return result.scalar_one()


    async def get_count_users_between(self, start_date: datetime, end_date: datetime) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(User.created_at >= start_date, User.created_at < end_date)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

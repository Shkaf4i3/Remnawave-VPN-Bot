from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..model import Tariff


class TariffRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def save_tariff(self, tariff: Tariff) -> Tariff:
        self.session.add(instance=tariff)
        await self.session.flush()
        await self.session.refresh(instance=tariff)
        return tariff


    async def get_tariff_by_id(self, tariff_id: str) -> Tariff | None:
        stmt = select(Tariff).where(Tariff.id == tariff_id)
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def get_tariff_by_name(self, name: str) -> Tariff | None:
        stmt = select(Tariff).where(Tariff.name == name)
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def get_list_tariffs(self) -> list[Tariff]:
        stmt = select(Tariff)
        result = await self.session.execute(statement=stmt)
        return result.scalars().unique().all()

from typing import Any

from ..dto import TariffDto
from ..model import Tariff
from ..mappings import tariff_mappings
from ..repo import TariffRepo, UnitOfWork, transactional
from .cache import CacheService


class TariffService:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        tariff_repo: TariffRepo,
        cache_service: CacheService,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.tariff_repo = tariff_repo
        self.cache_service = cache_service


    async def _internal_get_list_tariffs(self) -> list[dict[str, Any]]:
        tariffs = await self.tariff_repo.get_list_tariffs()
        return [
            tariff_mappings.map_tariff(tariff=tariff).model_dump(mode='json')
            for tariff in tariffs
        ]


    async def _internal_get_tariff_by_name(self, name: str) -> dict[str, Any]:
        existing_tariff = await self.tariff_repo.get_tariff_by_name(name=name)
        return tariff_mappings.map_tariff(tariff=existing_tariff).model_dump(mode="json")


    async def _internal_get_tariff_by_tariff_id(self, tariff_id: str) -> dict[str, Any]:
        existing_tariff = await self.tariff_repo.get_tariff_by_id(tariff_id=tariff_id)
        return tariff_mappings.map_tariff(tariff=existing_tariff).model_dump(mode="json")


    @transactional
    async def save_tariff(
        self,
        name: str,
        duration_days: int,
        price: float,
        device_limit: int,
        remnawave_squad_id: str | None = None,
        description: str | None = None,
    ) -> TariffDto | None:
        existing_tariff = await self.tariff_repo.get_tariff_by_name(name=name)
        if existing_tariff:
            return None
        new_tariff = Tariff(
            name=name,
            description=description,
            duration_days=duration_days,
            price=price,
            device_limit=device_limit,
            remnawave_squad_id=remnawave_squad_id,
        )
        saved_tariff = await self.tariff_repo.save_tariff(tariff=new_tariff)
        return tariff_mappings.map_tariff(tariff=saved_tariff)


    async def get_tariff_by_name(self, name: str) -> TariffDto:
        cached = await self.cache_service.get_value(key=f"tariff:info:{name}")
        if cached is not None:
            return TariffDto(**cached)
        existing_tariff = await self._internal_get_tariff_by_name(name=name)
        await self.cache_service.set_value(
            key=f"tariff:info:{name}",
            value=existing_tariff,
            ttl=600,
        )
        return TariffDto(**existing_tariff)


    async def get_tariff_by_tariff_id(self, tariff_id: str) -> TariffDto:
        cached = await self.cache_service.get_value(key=f"tariff:info:subs:{tariff_id}")
        if cached is not None:
            return TariffDto(**cached)
        existing_tariff = await self._internal_get_tariff_by_tariff_id(tariff_id=tariff_id)
        await self.cache_service.set_value(
            key=f"tariff:info:subs:{tariff_id}",
            value=existing_tariff,
            ttl=600,
        )
        return TariffDto(**existing_tariff)


    async def get_list_tariffs(self) -> list[TariffDto]:
        cached = await self.cache_service.get_value(key="tariffs:active")
        if cached is not None:
            return [TariffDto(**item) for item in cached]
        tariffs = await self._internal_get_list_tariffs()
        await self.cache_service.set_value(
            key="tariffs:active",
            value=tariffs,
            ttl=600,
        )
        return [TariffDto(**item) for item in tariffs]

from datetime import datetime, timezone, timedelta
from uuid import UUID
from typing import Any

from remnawave import RemnawaveSDK
from remnawave.models import (
    CreateUserRequestDto,
    CreateUserResponseDto,
    DeleteUserHwidDeviceResponseDto,
    HWIDDeleteRequest,
    UpdateUserRequestDto,
    GetUserByShortUuidResponseDto,
)
from remnawave.models.hwid import HwidDeviceDto
from remnawave.enums import UserStatus, TrafficLimitStrategy

from ..core import settings
from ..service import CacheService


class RemnawaveClient:
    def __init__(self, cache_service: CacheService) -> None:
        self.remnawave_client = RemnawaveSDK(
            base_url=settings.remnawave_url_panel,
            token=settings.remnawave_api_key,
        )
        self.cache_service = cache_service


    async def _internal_get_internal_squads(self) -> list[UUID]:
        squads = await self.remnawave_client.internal_squads.get_internal_squads()
        squads_list = squads.internal_squads
        return [squad.uuid for squad in squads_list]


    async def _internal_get_user_active_devices(self, uuid: str) -> list[dict[str, Any]]:
        devices = await self.remnawave_client.hwid.get_hwid_user(uuid)
        return [device.model_dump(mode="json") for device in devices.devices]


    async def get_internal_squads(self) -> list[UUID]:
        cached = await self.cache_service.get_value(key="remnawave_squads:all")
        if cached is not None:
            return cached
        squads = await self._internal_get_internal_squads()
        await self.cache_service.set_value(
            key="remnawave_squads:all",
            value=squads,
            ttl=1800,
        )
        return squads


    async def create_new_user(
        self,
        username: str,
        expire_at: datetime,
        traffic_limit_strategy: TrafficLimitStrategy | None = TrafficLimitStrategy.NO_RESET,
        telegram_id: str | None = None,
        hwid_device_limit: int | None = None,
    ) -> CreateUserResponseDto:
        active_internal_squads = await self.get_internal_squads()
        new_user = CreateUserRequestDto(
            username=username,
            expire_at=expire_at,
            status=UserStatus.ACTIVE,
            traffic_limit_strategy=traffic_limit_strategy,
            telegram_id=telegram_id,
            active_internal_squads=active_internal_squads,
            hwid_device_limit=hwid_device_limit,
        )
        response = await self.remnawave_client.users.create_user(new_user)
        return response


    async def get_subscription_url_by_user_uuid(self, user_uuid: UUID) -> str | Any:
        subscription = await self.remnawave_client.subscription.get_subscription_info_by_short_uuid(
            user_uuid
        )
        return subscription.subscription_url


    async def get_subscription_info_by_short_uuid(
        self,
        short_uuid: str,
    ) -> GetUserByShortUuidResponseDto:
        return await self.remnawave_client.users.get_user_by_short_uuid(short_uuid)


    async def get_user_active_devices(self, uuid: str) -> list[HwidDeviceDto]:
        cached = await self.cache_service.get_value(key=f"remnawave_devices:all:{uuid}")
        if cached is not None:
            return [
                HwidDeviceDto.model_validate(obj=item, by_alias=True, by_name=True)
                for item in cached
            ]
        devices = await self._internal_get_user_active_devices(uuid=uuid)
        await self.cache_service.set_value(
            key=f"remnawave_devices:all:{uuid}",
            value=devices,
            ttl=180,
        )
        return [
            HwidDeviceDto.model_validate(obj=device, by_alias=True, by_name=True)
            for device in devices
        ]


    async def delete_hwid_device_user(self, user_uuid: UUID, hwid: str) -> DeleteUserHwidDeviceResponseDto:
        dto = HWIDDeleteRequest(user_uuid=user_uuid, hwid=hwid)
        await self.cache_service.delete_key(key=f"remnawave_devices:all:{user_uuid}")
        return await self.remnawave_client.hwid.delete_hwid_to_user(dto)


    async def update_subscription_days(
        self,
        uuid: UUID,
        expires_at: datetime,
    ) -> None :
        dto = UpdateUserRequestDto(
            uuid=uuid,
            expire_at=expires_at,
        )
        await self.remnawave_client.users.update_user(dto)

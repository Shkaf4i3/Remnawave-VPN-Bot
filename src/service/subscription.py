from datetime import datetime
from uuid import UUID

from ..dto import SubscriptionDto
from ..model import Subscription, SubscriptionStatus
from ..mappings import subscription_mappings
from ..repo import SubscriptionRepo, UnitOfWork, transactional


class SubscriptionService:
    def __init__(self, unit_of_work: UnitOfWork, subscription_repo: SubscriptionRepo) -> None:
        self.unit_of_work = unit_of_work
        self.subscription_repo = subscription_repo


    @transactional
    async def save_subscription(
        self,
        user_id: str,
        tariff_id: str,
        expires_at: datetime,
        remnawave_user_uuid: UUID | None = None,
        remnawave_short_uuid: str | None = None,
        config_url: str | None = None,
    ) -> SubscriptionDto:
        new_subscription = Subscription(
            user_id=user_id,
            tariff_id=tariff_id,
            remnawave_user_uuid=remnawave_user_uuid,
            remnawave_short_uuid=remnawave_short_uuid,
            config_url=config_url,
            expires_at=expires_at,
        )
        saved_subscription = await self.subscription_repo.save_subscription(
            subscription=new_subscription,
        )
        return subscription_mappings.map_subscription(subscription=saved_subscription)


    async def get_subscription_by_user_id(self, user_id: int) -> SubscriptionDto | None:
        existing_subscription = await self.subscription_repo.get_subscription_by_user_id(
            user_id=user_id,
        )
        if not existing_subscription:
            return None
        return subscription_mappings.map_subscription(subscription=existing_subscription)


    async def get_subscription_by_id(self, id: str) -> SubscriptionDto | None:
        existing_subscription = await self.subscription_repo.get_subscription_by_id(
            subscription_id=id,
        )
        if not existing_subscription:
            return None
        return subscription_mappings.map_subscription(subscription=existing_subscription)


    async def get_active_subscriptions(self) -> list[SubscriptionDto]:
        subscriptions = await self.subscription_repo.get_active_subscriptions()
        return [
            subscription_mappings.map_subscription(subscription=subscription)
            for subscription in subscriptions
        ]


    @transactional
    async def update_subscription(
        self,
        id: str,
        expires_at: datetime | None = None,
        updated_at: datetime | None = None,
        config_url: str | None = None,
        remnawave_user_uuid: UUID | None = None,
        status: SubscriptionStatus | None = None,
    ) -> SubscriptionDto | None:
        existing_subscription = await self.subscription_repo.get_subscription_by_id(
            subscription_id=id,
        )
        if not existing_subscription:
            return None
        if expires_at:
            existing_subscription.expires_at = expires_at
        if updated_at:
            existing_subscription.updated_at = updated_at
        if config_url:
            existing_subscription.config_url = config_url
        if remnawave_user_uuid:
            existing_subscription.remnawave_user_uuid = remnawave_user_uuid
        if status:
            existing_subscription.status = status
        saved_subscription = await self.subscription_repo.save_subscription(
            subscription=existing_subscription,
        )
        return subscription_mappings.map_subscription(subscription=saved_subscription)

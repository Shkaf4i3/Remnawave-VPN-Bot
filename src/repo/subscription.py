from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..model import Subscription, SubscriptionStatus


class SubscriptionRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def save_subscription(self, subscription: Subscription) -> Subscription:
        self.session.add(instance=subscription)
        await self.session.flush()
        await self.session.refresh(instance=subscription)
        return subscription


    async def get_subscription_by_id(self, subscription_id: str) -> Subscription | None:
        stmt = select(Subscription).where(Subscription.id == subscription_id)
        result = await self.session.execute(statement=stmt)
        return result.scalar()

    async def get_subscription_by_user_id(self, user_id: str) -> Subscription | None:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def get_active_subscriptions(self) -> list[Subscription]:
        stmt = (
            select(Subscription)
            .where(Subscription.status == SubscriptionStatus.ACTIVE)
        )
        result = await self.session.execute(statement=stmt)
        return result.scalars().unique().all()

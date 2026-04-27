from ..dto import SubscriptionDto
from ..model import Subscription


def map_subscription(subscription: Subscription) -> SubscriptionDto:
    return SubscriptionDto(
        id=subscription.id,
        user_id=subscription.user_id,
        tariff_id=subscription.tariff_id,
        status=subscription.status,
        expires_at=subscription.expires_at,
        remnawave_user_uuid=subscription.remnawave_user_uuid,
        remnawave_short_uuid=subscription.remnawave_short_uuid,
        config_url=subscription.config_url,
        updated_at=subscription.updated_at,
        created_at=subscription.created_at,
    )

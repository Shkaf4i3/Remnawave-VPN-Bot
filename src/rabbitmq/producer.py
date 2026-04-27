from faststream.rabbit import RabbitExchange, ExchangeType

from ..core import settings
from ..service import UserService
from ..mappings import mailing_mappings
from ..client import broker


direct_exchange = RabbitExchange(
    name="notifications",
    type=ExchangeType.DIRECT,
    durable=True,
)


async def mailing_message_to_users(
    user_service: UserService,
    message_type: str,
    message_text: str | None = None,
    message_media: str| None = None,
) -> None:
    available_users = await user_service.get_list_users()
    for user in available_users:
        if user.tg_id in settings.admin_ids:
            continue
        task = mailing_mappings.mapping_mailing(
            user=user,
            message_type=message_type,
            message_text=message_text,
            message_media=message_media,
        )
        await broker.publish(
            message=task,
            exchange=direct_exchange,
            routing_key="tg_id",
            persist=True,
        )

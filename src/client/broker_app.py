from faststream.rabbit.broker import RabbitBroker

from ..core import settings


broker = RabbitBroker(url=settings.rabbitmq_url)

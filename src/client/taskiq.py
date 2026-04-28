from taskiq_faststream import BrokerWrapper, StreamScheduler
from taskiq.schedule_sources import LabelScheduleSource

from .broker_app import broker


taskiq_scheduler = BrokerWrapper(broker=broker)


taskiq_scheduler.task(
    schedule=[
        {
            "cron": "01 00 * * *",
        },
    ],
    queue="schedule_subs",
)


scheduler = StreamScheduler(
    broker=taskiq_scheduler,
    sources=[LabelScheduleSource(broker=taskiq_scheduler)],
)

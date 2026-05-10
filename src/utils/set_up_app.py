from contextlib import asynccontextmanager
from logging import basicConfig, INFO, getLogger
from typing import Any, AsyncGenerator

from aiogram.types import BotCommandScopeAllPrivateChats
from fastapi import FastAPI
from aiohttp import ClientSession, ClientTimeout

from ..app import bot, dp
from ..core import settings, db_helper
from ..model import Base, Tariff
from ..repo import UnitOfWork, UserRepo, TariffRepo
from ..service import UserService, TariffService, CacheService
from ..aiogram_functions import CallbackAnswer, available_commands
from ..client import RemnawaveClient, broker, redis
from ..rabbitmq import schedule_queue, mailing_queue, direct_exchange, api_queue


logger = getLogger(name=__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[Any, Any]:
    basicConfig(
        level=INFO,
        datefmt=r"%Y-%m-%d %H:%M:%S",
        format=r"[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
    )
    cache_service = CacheService(redis=redis, default_ttl=300)
    remnawave_client = RemnawaveClient(cache_service=cache_service)
    await bot.set_webhook(
        url=settings.tg_webhook_url,
        drop_pending_updates=True,
        secret_token=settings.secret_token,
    )
    exists_commands = await bot.get_my_commands(scope=BotCommandScopeAllPrivateChats())
    if not exists_commands:
        await bot.set_my_commands(
            commands=available_commands,
            scope=BotCommandScopeAllPrivateChats(),
        )
    timeout = ClientTimeout(total=5)
    async with ClientSession(timeout=timeout) as session:
        broker.context.set_global(key="cache_service", v=cache_service)
        broker.context.set_global(key="session", v=session)
        broker.context.set_global(key="bot", v=bot)
        broker.context.set_global(key="remnawave_client", v=remnawave_client)
        await broker.start()
        await broker.declare_exchange(exchange=direct_exchange)
        await broker.declare_queue(queue=mailing_queue)
        await broker.declare_queue(queue=schedule_queue)
        await broker.declare_queue(queue=api_queue)
        # We import the task lazily to avoid cyclical imports.
        from ..handlers import user_router, admin_router
        dp.include_routers(
            user_router,
            admin_router,
        )
        dp.callback_query.middleware(CallbackAnswer())
        dp["cache"] = cache_service
        dp["remnawave_client"] = remnawave_client
        async with db_helper.session_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with db_helper.session_factory() as session:
            squad_id = await remnawave_client.get_internal_squads()
            unit_of_work = UnitOfWork(session=session)
            user_repo = UserRepo(session=session)
            tariff_repo = TariffRepo(session=session)
            tariff_service = TariffService(
                unit_of_work=unit_of_work,
                tariff_repo=tariff_repo,
                cache_service=cache_service,
            )
            user_service = UserService(
                unit_of_work=unit_of_work,
                user_repo=user_repo,
                cache_service=cache_service,
            )
            await user_service.create_admin_on_startup()
            tariffs = [
                Tariff(
                    name="Пробный (Trial)",
                    description="Для ознакомления с сервисом",
                    duration_days=3,
                    price=50,
                    device_limit=1,
                    remnawave_squad_id=str(squad_id[0]),
                ),
                Tariff(
                    name="Базовый (Basic)",
                    description="Для повседневного сёрфинга",
                    duration_days=30,
                    price=200,
                    device_limit=2,
                    remnawave_squad_id=str(squad_id[0]),
                ),
                Tariff(
                    name="Оптимальный (Optimal)",
                    description="Активное использование (загрузки, онлайн игры)",
                    duration_days=30,
                    price=400,
                    device_limit=3,
                    remnawave_squad_id=str(squad_id[0]),
                ),
                Tariff(
                    name="Максимальный (Max)",
                    description="Семейный или корпоративный доступ",
                    duration_days=90,
                    price=800,
                    device_limit=5,
                    remnawave_squad_id=str(squad_id[0]),
                ),
            ]
            for tariff in tariffs:
                existing_tariff = await tariff_repo.get_tariff_by_name(name=tariff.name)
                if not existing_tariff:
                    await tariff_service.save_tariff(
                        name=tariff.name,
                        duration_days=tariff.duration_days,
                        price=tariff.price,
                        device_limit=tariff.device_limit,
                        remnawave_squad_id=tariff.remnawave_squad_id,
                        description=tariff.description,
                    )
        yield
        broker.context.reset_global(key="bot")
        broker.context.reset_global(key="session")
        broker.context.reset_global(key="cache_service")
        broker.context.reset_global(key="remnawave_client")
        await broker.stop()
        await bot.session.close()

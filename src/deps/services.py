from typing import Annotated

from fastapi import Depends

from ..repo import UserRepo, UnitOfWork, PaymentRepo, TariffRepo, SubscriptionRepo
from ..service import (
    UserService,
    PaymentService,
    WebhookService,
    TariffService,
    SubscriptionService,
    AnalyticsService,
    CacheService,
)
from .repos import (
    get_unit_of_work,
    get_user_repo,
    get_payment_repo,
    get_tariff_repo,
    get_subscription_repo,
)
from .clients import get_crypto_bot, get_heleket, get_lolz_team
from ..client import redis, CryptoBot, LolzTeam, Heleket, PaymentSystem


def get_payment_system(
    crypto_bot: Annotated[CryptoBot, Depends(get_crypto_bot)],
    lolz_client: Annotated[LolzTeam, Depends(get_lolz_team)],
    heleket_client: Annotated[Heleket, Depends(get_heleket)],
) -> PaymentSystem:
    return PaymentSystem(
        crypto_bot=crypto_bot,
        lolz_client=lolz_client,
        heleket_client=heleket_client,
    )


def get_cache_service() -> CacheService:
    return CacheService(redis=redis, default_ttl=300)


def get_user_service(
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
) -> UserService:
    return UserService(
        unit_of_work=unit_of_work,
        user_repo=user_repo,
        cache_service=cache_service,
    )


def get_payment_service(
    payment_repo: Annotated[PaymentRepo, Depends(get_payment_repo)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> PaymentService:
    return PaymentService(unit_of_work=unit_of_work, payment_repo=payment_repo)


def get_tariff_service(
    tariff_repo: Annotated[TariffRepo, Depends(get_tariff_repo)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
) -> TariffService:
    return TariffService(
        unit_of_work=unit_of_work,
        tariff_repo=tariff_repo,
        cache_service=cache_service,
    )


def get_subscription_service(
    subscription_repo: Annotated[SubscriptionRepo, Depends(get_subscription_repo)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> SubscriptionService:
    return SubscriptionService(
        unit_of_work=unit_of_work,
        subscription_repo=subscription_repo,
    )


def get_analytics_service(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    payment_repo: Annotated[PaymentRepo, Depends(get_payment_repo)],
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
) -> AnalyticsService:
    return AnalyticsService(
        unit_of_work=unit_of_work,
        user_repo=user_repo,
        payment_repo=payment_repo,
        cache_service=cache_service,
    )


def get_webhook_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    tariff_service: Annotated[TariffService, Depends(get_tariff_service)],
    subscription_service: Annotated[SubscriptionService, Depends(get_subscription_service)],
    analytics_service: Annotated[AnalyticsService, Depends(get_analytics_service)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
    payment_system: Annotated[PaymentSystem, Depends(get_payment_system)],
) -> WebhookService:
    return WebhookService(
        user_service=user_service,
        payment_service=payment_service,
        tariff_service=tariff_service,
        subscription_service=subscription_service,
        analytics_service=analytics_service,
        cache_service=cache_service,
        payment_system=payment_system,
    )

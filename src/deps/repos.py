from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..repo import UserRepo, UnitOfWork, PaymentRepo, TariffRepo, SubscriptionRepo
from .session import open_session


def get_user_repo(session: Annotated[AsyncSession, Depends(open_session)]) -> UserRepo:
    return UserRepo(session=session)


def get_payment_repo(session: Annotated[AsyncSession, Depends(open_session)]) -> PaymentRepo:
    return PaymentRepo(session=session)


def get_tariff_repo(session: Annotated[AsyncSession, Depends(open_session)]) -> TariffRepo:
    return TariffRepo(session=session)


def get_subscription_repo(
    session: Annotated[AsyncSession, Depends(open_session)],
) -> SubscriptionRepo:
    return SubscriptionRepo(session=session)


def get_unit_of_work(session: Annotated[AsyncSession, Depends(open_session)]) -> UnitOfWork:
    return UnitOfWork(session=session)

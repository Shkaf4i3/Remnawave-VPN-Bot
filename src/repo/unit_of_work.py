from contextlib import asynccontextmanager
from functools import wraps
from typing import TypeVar, Callable, Awaitable, ParamSpec, Concatenate, Protocol

from sqlalchemy.ext.asyncio import AsyncSession


P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T", bound="HasUnitOfWork")


class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    @asynccontextmanager
    async def transaction(self):
        try:
            yield self.session
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e


def transactional(
    method: Callable[Concatenate[T, P], Awaitable[R]],
) -> Callable[Concatenate[T, P], Awaitable[R]]:
    @wraps(method)
    async def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        if not hasattr(self, "unit_of_work"):
            raise AttributeError("Unit of Work not initialized.")
        async with self.unit_of_work.transaction():
            return await method(self, *args, **kwargs)
    return wrapper


class HasUnitOfWork(Protocol):
    """Protocol for classes with the unit_of_work attribute."""
    unit_of_work: UnitOfWork

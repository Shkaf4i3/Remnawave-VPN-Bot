from orjson import loads, dumps
from typing import Any, Callable, Coroutine

from redis.asyncio import Redis


class CacheService:
    def __init__(self, redis: Redis, default_ttl: int = 300) -> None:
        self.redis = redis
        self.default_ttl = default_ttl


    async def get_value(self, key: str) -> Any | None:
        raw = await self.redis.get(name=key)
        if raw is None:
            return None
        return loads(raw)


    async def set_value(self, key: str, value: Any, ttl: int | None = None) -> None:
        ttl = ttl or self.default_ttl
        await self.redis.set(name=key, value=dumps(value), ex=ttl)


    async def delete_key(self, key: str) -> None:
        await self.redis.delete(key)


    async def remember_value(
        self,
        key: str,
        callback: Callable[[], Coroutine[Any, Any, Any]],
        ttl: int | None = None,
    ) -> Any:
        cached = await self.get_value(key=key)
        if cached is not None:
            return cached
        value = await callback()
        await self.set_value(key=key, value=value, ttl=ttl)
        return value

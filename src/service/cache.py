from orjson import loads, dumps
from typing import Any

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
        if ttl is None:
            ttl = self.default_ttl
        if ttl > 0:
            await self.redis.set(name=key, value=dumps(value), ex=ttl)
        else:
            await self.redis.set(name=key, value=dumps(value))


    async def delete_key(self, key: str) -> None:
        await self.redis.delete(key)

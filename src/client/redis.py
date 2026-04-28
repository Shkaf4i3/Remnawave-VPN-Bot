from redis.asyncio import Redis

from ..core import settings


redis = Redis.from_url(url=settings.redis_url, decode_responses=True)

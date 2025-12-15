from __future__ import annotations

from redis.asyncio import Redis


class RedisPromoCodeRepository:
    def __init__(self, client: Redis, prefix: str = "promo") -> None:
        self._client = client
        self._prefix = prefix

    async def reserve(self, code: str, ttl_seconds: int) -> bool:
        key = f"{self._prefix}:{code}"
        return bool(
            await self._client.set(name=key, value="1", ex=ttl_seconds, nx=True)
        )

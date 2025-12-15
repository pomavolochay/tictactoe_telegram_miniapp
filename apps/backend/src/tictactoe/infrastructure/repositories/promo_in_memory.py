from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from typing import Dict


class InMemoryPromoCodeRepository:
    def __init__(self) -> None:
        self._storage: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def reserve(self, code: str, ttl_seconds: int) -> bool:
        async with self._lock:
            self._purge()
            now = time.time()
            if code in self._storage and self._storage[code] > now:
                return False
            self._storage[code] = now + ttl_seconds
            return True

    def _purge(self) -> None:
        now = time.time()
        expired = [code for code, expires_at in self._storage.items() if expires_at <= now]
        for code in expired:
            del self._storage[code]

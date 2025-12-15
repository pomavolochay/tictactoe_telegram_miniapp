from __future__ import annotations

import random
import string
from dataclasses import dataclass

from ..interfaces import MetricsRecorder, PromoCodeRepository

ALPHABET = string.ascii_uppercase + string.digits


class PromoCodeGenerationError(RuntimeError):
    """Raised when the application cannot create a unique promo code."""


@dataclass(slots=True)
class PromoCodeService:
    repository: PromoCodeRepository
    metrics: MetricsRecorder
    ttl_days: int = 30
    code_length: int = 5
    max_attempts: int = 10

    async def generate_unique_code(self) -> str:
        ttl_seconds = self.ttl_days * 24 * 60 * 60
        for _ in range(self.max_attempts):
            candidate = self._random_code()
            stored = await self.repository.reserve(candidate, ttl_seconds)
            if stored:
                self.metrics.inc_promo_generated()
                return candidate
            self.metrics.inc_promo_duplicate_prevented()
        self.metrics.inc_promo_generation_failure()
        raise PromoCodeGenerationError("Unable to generate a unique promo code")

    def _random_code(self) -> str:
        return "".join(random.choice(ALPHABET) for _ in range(self.code_length))

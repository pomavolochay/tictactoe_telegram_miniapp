import pytest

from tictactoe.application.services import PromoCodeGenerationError, PromoCodeService
from tictactoe.infrastructure.metrics import MetricsAdapter
from tictactoe.infrastructure.repositories import InMemoryPromoCodeRepository


class DummyMetrics(MetricsAdapter):
    def __init__(self) -> None:
        super().__init__()
        self.generated = 0
        self.duplicates = 0
        self.failures = 0

    def inc_promo_generated(self) -> None:
        self.generated += 1

    def inc_promo_duplicate_prevented(self) -> None:
        self.duplicates += 1

    def inc_promo_generation_failure(self) -> None:
        self.failures += 1


@pytest.mark.anyio
async def test_promo_code_uniqueness() -> None:
    repo = InMemoryPromoCodeRepository()
    metrics = DummyMetrics()
    service = PromoCodeService(repository=repo, metrics=metrics, ttl_days=1)

    code = await service.generate_unique_code()
    assert len(code) == 5
    assert metrics.generated == 1

    # Force duplicate by patching _random_code
    service._random_code = lambda: code  # type: ignore[assignment]
    with pytest.raises(PromoCodeGenerationError):
        await service.generate_unique_code()
    assert metrics.duplicates >= 1

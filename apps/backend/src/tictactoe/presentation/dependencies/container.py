from __future__ import annotations

from functools import lru_cache
from typing import Iterable

from fastapi import Depends
from redis.asyncio import Redis, from_url as redis_from_url

from ...application.interfaces import PromoCodeRepository
from ...application.services import PromoCodeService, TelegramNotificationService
from ...application.use_cases import MakeMoveUseCase, ResetGameUseCase, TelegramWebhookUseCase
from ...config import Settings, get_settings
from ...domain.services.ai import MinimaxAIService
from ...infrastructure.metrics import MetricsAdapter
from ...infrastructure.repositories import InMemoryPromoCodeRepository, RedisPromoCodeRepository
from ...infrastructure.telegram.client import NullTelegramClient, TelegramBotClient

_memory_repo = InMemoryPromoCodeRepository()
_redis_repo: RedisPromoCodeRepository | None = None
_redis_client: Redis | None = None
_current_redis_url: str | None = None


@lru_cache(maxsize=1)
def get_metrics() -> MetricsAdapter:
    return MetricsAdapter()


@lru_cache(maxsize=1)
def get_ai_service() -> MinimaxAIService:
    return MinimaxAIService()


def get_promo_repository(settings: Settings = Depends(get_settings)) -> PromoCodeRepository:
    global _redis_repo, _redis_client, _current_redis_url
    if settings.redis_url:
        if _redis_repo and _current_redis_url == settings.redis_url:
            return _redis_repo
        _redis_client = redis_from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        _redis_repo = RedisPromoCodeRepository(_redis_client)
        _current_redis_url = settings.redis_url
        return _redis_repo
    return _memory_repo


def get_promo_service(
    repository: PromoCodeRepository = Depends(get_promo_repository),
    metrics: MetricsAdapter = Depends(get_metrics),
    settings: Settings = Depends(get_settings),
) -> PromoCodeService:
    return PromoCodeService(
        repository=repository,
        metrics=metrics,
        ttl_days=settings.promo_code_ttl_days,
        code_length=settings.promo_code_length,
    )


def get_telegram_client(settings: Settings = Depends(get_settings)) -> TelegramBotClient | NullTelegramClient:
    if not settings.telegram_bot_token:
        return NullTelegramClient()
    return TelegramBotClient(settings.telegram_bot_token)


def get_telegram_service(
    client=Depends(get_telegram_client),
    metrics: MetricsAdapter = Depends(get_metrics),
    settings: Settings = Depends(get_settings),
) -> TelegramNotificationService:
    chat_ids: Iterable[str] = settings.telegram_chat_ids
    return TelegramNotificationService(client=client, metrics=metrics, chat_ids=chat_ids)


def get_make_move_use_case(
    ai_service: MinimaxAIService = Depends(get_ai_service),
    promo_service: PromoCodeService = Depends(get_promo_service),
    telegram_service: TelegramNotificationService = Depends(get_telegram_service),
    metrics: MetricsAdapter = Depends(get_metrics),
    settings: Settings = Depends(get_settings),
) -> MakeMoveUseCase:
    return MakeMoveUseCase(
        ai_service=ai_service,
        promo_service=promo_service,
        telegram_service=telegram_service,
        metrics=metrics,
        ai_mistake_probability=settings.ai_mistake_probability,
    )


def get_reset_game_use_case() -> ResetGameUseCase:
    return ResetGameUseCase()


def get_telegram_webhook_use_case(
    client=Depends(get_telegram_client),
    settings: Settings = Depends(get_settings),
) -> TelegramWebhookUseCase:
    return TelegramWebhookUseCase(client=client, settings=settings)

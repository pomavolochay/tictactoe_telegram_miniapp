from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Literal, Sequence

import structlog

from ..interfaces import MetricsRecorder, TelegramClient

logger = structlog.get_logger()

NotificationType = Literal["win", "lose"]


@dataclass(frozen=True, slots=True)
class TelegramNotificationService:
    """
    Sends game outcome notifications to Telegram chats.

    Design goals:
    - never break gameplay if Telegram is down;
    - send concurrently to multiple targets;
    - record success/failure counters and latency metrics;
    - deduplicate targets deterministically.
    """

    client: TelegramClient
    metrics: MetricsRecorder
    chat_ids: Sequence[str]

    async def notify_win(self, promo_code: str, chat_id: str | None = None) -> None:
        await self._send_to_targets(
            text=f"Победа! Промокод выдан: {promo_code}",
            notification_type="win",
            preferred_chat_id=chat_id,
        )

    async def notify_loss(self, chat_id: str | None = None) -> None:
        await self._send_to_targets(
            text="Проигрыш",
            notification_type="lose",
            preferred_chat_id=chat_id,
        )

    async def _send_to_targets(
        self,
        *,
        text: str,
        notification_type: NotificationType,
        preferred_chat_id: str | None,
    ) -> None:
        targets = self._resolve_targets(preferred_chat_id)
        if not targets:
            logger.info("telegram_notification_skipped", reason="no_chat_id")
            return

        await asyncio.gather(
            *(self._send_one(chat_id=t, text=text, notification_type=notification_type) for t in targets),
            return_exceptions=True,
        )

    def _resolve_targets(self, preferred_chat_id: str | None) -> list[str]:
        raw: list[str] = []
        if preferred_chat_id:
            raw.append(preferred_chat_id)
        raw.extend(self.chat_ids)

        seen: set[str] = set()
        targets: list[str] = []

        for chat_id in raw:
            normalized = (chat_id or "").strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            targets.append(normalized)

        return targets

    async def _send_one(self, *, chat_id: str, text: str, notification_type: NotificationType) -> None:
        start = time.perf_counter()
        try:
            await self.client.send_message(chat_id=chat_id, text=text)
        except Exception as exc:  # pragma: no cover
            logger.warning(
                "telegram_notification_failed",
                chat_id=chat_id,
                notification_type=notification_type,
                error=str(exc),
            )
            try:
                self.metrics.inc_telegram_notification_failure()
            except Exception:  # pragma: no cover
                logger.exception("telegram_metrics_failure_increment_failed")
            return
        finally:
            elapsed = time.perf_counter() - start
            try:
                self.metrics.observe_telegram_notification(elapsed)
            except Exception:  # pragma: no cover
                logger.exception("telegram_metrics_latency_observe_failed")

        try:
            self.metrics.inc_telegram_notification(notification_type)
        except Exception:  # pragma: no cover
            logger.exception("telegram_metrics_success_increment_failed")

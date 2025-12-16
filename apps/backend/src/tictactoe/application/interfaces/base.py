from __future__ import annotations

from typing import Protocol


class PromoCodeRepository(Protocol):
    async def reserve(self, code: str, ttl_seconds: int) -> bool:
        """Try to persist the code for ttl_seconds.

        Returns True when the code was stored (i.e. unique) and False when the code already existed.
        """


class TelegramClient(Protocol):
    async def send_message(self, *, chat_id: str, text: str, reply_markup: dict | None = None) -> None:
        """Send a Telegram message to chat_id."""

    async def send_photo(
        self,
        *,
        chat_id: str,
        photo_path: str,
        caption: str,
        reply_markup: dict | None = None,
        parse_mode: str = "HTML",
    ) -> None:
        """Send a Telegram photo with optional caption to chat_id."""


class MetricsRecorder(Protocol):
    def inc_games_started(self) -> None: ...

    def inc_games_finished(self, result: str) -> None: ...

    def inc_moves(self, actor: str) -> None: ...

    def inc_invalid_move(self, reason: str) -> None: ...

    def observe_ai_compute(self, duration_seconds: float) -> None: ...

    def inc_promo_generated(self) -> None: ...

    def inc_promo_duplicate_prevented(self) -> None: ...

    def inc_promo_generation_failure(self) -> None: ...

    def inc_telegram_notification(self, notification_type: str) -> None: ...

    def inc_telegram_notification_failure(self, notification_type: str) -> None: ...

    def observe_telegram_notification(self, duration_seconds: float) -> None: ...

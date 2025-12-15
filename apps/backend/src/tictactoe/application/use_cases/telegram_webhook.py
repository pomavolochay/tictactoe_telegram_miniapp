from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import structlog

from ...config import Settings
from ..interfaces import TelegramClient

logger = structlog.get_logger()


@dataclass(frozen=True, slots=True)
class TelegramWebhookUseCase:
    client: TelegramClient
    settings: Settings

    async def handle_update(self, update: Mapping[str, Any]) -> None:
        """Handle incoming Telegram updates."""
        message = self._extract_message(update)
        if not message:
            return

        chat_id = self._extract_chat_id(message)
        if chat_id is None:
            return

        text = self._extract_text(message)
        if not text:
            return

        if text.startswith("/start"):
            await self._send_welcome(chat_id=str(chat_id))

    def _extract_message(self, update: Mapping[str, Any]) -> Mapping[str, Any] | None:
        payload = update.get("message") or update.get("edited_message")
        return payload if isinstance(payload, Mapping) else None

    def _extract_chat_id(self, message: Mapping[str, Any]) -> int | None:
        chat = message.get("chat")
        if not isinstance(chat, Mapping):
            return None
        chat_id = chat.get("id")
        return chat_id if isinstance(chat_id, int) else None

    def _extract_text(self, message: Mapping[str, Any]) -> str:
        raw = message.get("text")
        return raw.strip().lower() if isinstance(raw, str) else ""

    async def _send_welcome(self, chat_id: str) -> None:
        url = self._resolve_webapp_url()
        reply_markup: dict[str, Any] = {
            "inline_keyboard": [
                [
                    {
                        "text": "Играть",
                        "web_app": {"url": self._append_chat_id(url, chat_id)},
                    }
                ]
            ]
        }
        text = (
            "Привет! Готова сыграть в уютный TicTacToe?\n"
            "Нажми на кнопку ниже - поле уже ждёт твой первый ход."
        )
        try:
            await self.client.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
            logger.info("telegram_welcome_sent", chat_id=chat_id)
        except Exception as exc:  # pragma: no cover
            logger.warning("telegram_welcome_send_failed", chat_id=chat_id, error=str(exc))

    def _resolve_webapp_url(self) -> str:
        origin = (self.settings.frontend_origin or "").strip()
        if origin:
            return origin
        domain = (self.settings.domain or "").strip()
        if domain:
            return f"https://{domain}"
        return "https://example.com"

    def _append_chat_id(self, url: str, chat_id: str) -> str:
        if not url:
            return url
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}chat_id={chat_id}"

from __future__ import annotations

from typing import Any, Dict

import httpx


class TelegramBotClient:
    def __init__(self, token: str, timeout: float = 5.0) -> None:
        self._client = httpx.AsyncClient(
            base_url=f"https://api.telegram.org/bot{token}",
            timeout=timeout,
        )

    async def send_message(
        self,
        *,
        chat_id: str,
        text: str,
        reply_markup: Dict[str, Any] | None = None,
    ) -> None:
        payload: Dict[str, Any] = {"chat_id": chat_id, "text": text}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        response = await self._client.post("/sendMessage", json=payload)
        response.raise_for_status()

    async def aclose(self) -> None:
        await self._client.aclose()


class NullTelegramClient:
    async def send_message(  # pragma: no cover - no-op fallback
        self,
        *,
        chat_id: str,
        text: str,
        reply_markup: Dict[str, Any] | None = None,
    ) -> None:
        return None

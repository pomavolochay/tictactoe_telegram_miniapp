from __future__ import annotations

from typing import Any, Dict

import httpx
import json
import structlog


logger = structlog.get_logger()


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
        _raise_for_telegram(response)

    async def send_photo(
        self,
        *,
        chat_id: str,
        photo_path: str,
        caption: str,
        reply_markup: Dict[str, Any] | None = None,
        parse_mode: str = "HTML",
    ) -> None:
        data: Dict[str, Any] = {"chat_id": chat_id, "caption": caption, "parse_mode": parse_mode}
        if reply_markup is not None:
            data["reply_markup"] = json.dumps(reply_markup)
        with open(photo_path, "rb") as fh:
            files = {"photo": (photo_path, fh, "image/png")}
            response = await self._client.post("/sendPhoto", data=data, files=files)
        _raise_for_telegram(response)

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

    async def send_photo(  # pragma: no cover - no-op fallback
        self,
        *,
        chat_id: str,
        photo_path: str,
        caption: str,
        reply_markup: Dict[str, Any] | None = None,
        parse_mode: str = "HTML",
    ) -> None:
        return None


def _raise_for_telegram(response: httpx.Response) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:  # pragma: no cover - network related
        try:
            payload = response.json()
        except Exception:
            payload = {"body": response.text}
        logger.warning("telegram_api_error", status=response.status_code, payload=payload)
        raise exc

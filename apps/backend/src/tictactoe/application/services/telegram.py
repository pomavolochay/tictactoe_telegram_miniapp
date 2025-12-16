from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

import structlog

from ...config import Settings
from ...infrastructure.telegram.assets import get_asset_path
from ..interfaces import MetricsRecorder, TelegramClient

logger = structlog.get_logger()

NotificationType = Literal["win", "lose", "welcome"]

WELCOME_CAPTION = (
    "<b>Привет! 🫶</b>\n\n"
    "Готова провести пару уютных минут за игрой?\n\n"
    "Это <b>TicTacToe</b>, где ты играешь против внимательного AI — "
    "без спешки, с настроением и маленькими победами.\n\n"
    "✨ Побеждай — и получай приятный промокод.\n\n"
    "Нажми кнопку ниже — поле уже ждёт твой первый ход."
)

WIN_CAPTION_TEMPLATE = (
    "<b>Поздравляю! 🎉</b>\n\n"
    "Ты сыграла идеально — партия осталась за тобой 🫶\n\n"
    "Вот твой персональный промокод:\n\n"
    "<code>{code}</code>\n\n"
    "Сохрани его и побалуй себя чем-нибудь приятным.\n\n"
    "Хочешь сыграть ещё раз?"
)

LOSE_CAPTION = (
    "<b>В этот раз не получилось 🫶</b>\n\n"
    "Но в таких партиях нет проигравших — есть только новые ходы и идеи.\n\n"
    "Сделаем реванш?\n"
    "Поле уже готово для новой игры."
)


@dataclass(frozen=True, slots=True)
class TelegramNotificationService:
    client: TelegramClient
    metrics: MetricsRecorder
    chat_ids: Sequence[str]
    settings: Settings

    async def notify_win(self, promo_code: str, chat_id: str | None = None) -> None:
        caption = WIN_CAPTION_TEMPLATE.format(code=promo_code)
        await self._send_to_targets(
            photo_name="win.png",
            caption=caption,
            notification_type="win",
            preferred_chat_id=chat_id,
            reply_markup=self._play_again_markup(chat_id or ""),
        )

    async def notify_loss(self, chat_id: str | None = None) -> None:
        await self._send_to_targets(
            photo_name="lose.png",
            caption=LOSE_CAPTION,
            notification_type="lose",
            preferred_chat_id=chat_id,
            reply_markup=self._play_again_markup(chat_id or ""),
        )

    async def notify_welcome(self, chat_id: str, reply_markup: dict) -> None:
        await self._send_to_targets(
            photo_name="welcome.png",
            caption=WELCOME_CAPTION,
            notification_type="welcome",
            preferred_chat_id=chat_id,
            reply_markup=reply_markup,
            allow_fallback_targets=False,
        )

    async def _send_to_targets(
        self,
        *,
        photo_name: str,
        caption: str,
        notification_type: NotificationType,
        preferred_chat_id: str | None,
        reply_markup: dict | None = None,
        allow_fallback_targets: bool = True,
    ) -> None:
        targets = self._resolve_targets(preferred_chat_id, allow_fallback_targets)
        if not targets:
            logger.info("telegram_notification_skipped", reason="no_chat_id", type=notification_type)
            return

        photo_path = self._resolve_asset(photo_name)

        await asyncio.gather(
            *(self._send_one(
                chat_id=target,
                photo_path=photo_path,
                caption=caption,
                notification_type=notification_type,
                reply_markup=reply_markup,
            ) for target in targets),
            return_exceptions=True,
        )

    def _resolve_targets(self, preferred_chat_id: str | None, allow_fallback: bool) -> list[str]:
        raw: list[str] = []
        if preferred_chat_id:
            raw.append(preferred_chat_id)
        if allow_fallback:
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

    def _play_again_markup(self, chat_id: str) -> dict | None:
        url = self._resolve_webapp_url()
        if not url:
            return None
        return {
            "inline_keyboard": [
                [
                    {
                        "text": "Играть снова",
                        "web_app": {"url": self._append_chat_id(url, chat_id)},
                    }
                ]
            ]
        }

    def _resolve_webapp_url(self) -> str:
        origin = (self.settings.frontend_origin or "").strip()
        if origin:
            return origin
        domain = (self.settings.domain or "").strip()
        if domain:
            return f"https://{domain}"
        return ""

    def _append_chat_id(self, url: str, chat_id: str) -> str:
        if not url or not chat_id:
            return url
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}chat_id={chat_id}"

    def _resolve_asset(self, photo_name: str) -> Path:
        # get_asset_path ожидается как функция, возвращающая Path
        path = get_asset_path(self.settings, photo_name)
        if not isinstance(path, Path):
            path = Path(str(path))

        if not path.exists() or not path.is_file():
            # Важно: не падаем — но фиксируем проблему (бот всё равно может жить)
            logger.warning("telegram_asset_missing", photo_name=photo_name, resolved=str(path))
        return path

    async def _send_one(
        self,
        *,
        chat_id: str,
        photo_path: Path,
        caption: str,
        notification_type: NotificationType,
        reply_markup: dict | None,
    ) -> None:
        start = time.perf_counter()
        ok = False

        try:
            await self.client.send_photo(
                chat_id=chat_id,
                photo_path=str(photo_path),
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
            ok = True
        except Exception as exc:  # pragma: no cover
            logger.warning(
                "telegram_notification_failed",
                chat_id=chat_id,
                notification_type=notification_type,
                error=str(exc),
            )
            self._safe_inc_failure(notification_type)
        finally:
            elapsed = time.perf_counter() - start
            self._safe_observe_latency(elapsed)

        if ok:
            self._safe_inc_success(notification_type)

    # ---- metrics guards (чтобы не падать от различий в интерфейсе) ----

    def _safe_inc_success(self, notification_type: NotificationType) -> None:
        try:
            self.metrics.inc_telegram_notification(notification_type)
        except TypeError:
            # если интерфейс старый и не принимает type
            try:
                self.metrics.inc_telegram_notification()
            except Exception:  # pragma: no cover
                logger.exception("telegram_metrics_success_increment_failed")
        except Exception:  # pragma: no cover
            logger.exception("telegram_metrics_success_increment_failed")

    def _safe_inc_failure(self, notification_type: NotificationType) -> None:
        try:
            self.metrics.inc_telegram_notification_failure(notification_type)
        except TypeError:
            # если интерфейс старый и не принимает type
            try:
                self.metrics.inc_telegram_notification_failure()
            except Exception:  # pragma: no cover
                logger.exception("telegram_metrics_failure_increment_failed")
        except Exception:  # pragma: no cover
            logger.exception("telegram_metrics_failure_increment_failed")

    def _safe_observe_latency(self, seconds: float) -> None:
        try:
            self.metrics.observe_telegram_notification(seconds)
        except Exception:  # pragma: no cover
            logger.exception("telegram_metrics_latency_observe_failed")

import pytest
from pathlib import Path

from tictactoe.application.services.telegram import TelegramNotificationService
from tictactoe.application.use_cases import TelegramWebhookUseCase
from tictactoe.config import Settings


class DummyClient:
    def __init__(self) -> None:
        self.photos: list[dict] = []

    async def send_photo(
        self,
        *,
        chat_id: str,
        photo_path: str,
        caption: str,
        reply_markup=None,
        parse_mode: str = "HTML",
    ) -> None:
        self.photos.append(
            {
                "chat_id": chat_id,
                "photo_path": photo_path,
                "caption": caption,
                "reply_markup": reply_markup,
                "parse_mode": parse_mode,
            }
        )


class DummyMetrics:
    def inc_games_started(self):
        ...

    def inc_games_finished(self, result: str):
        ...

    def inc_moves(self, actor: str):
        ...

    def inc_invalid_move(self, reason: str):
        ...

    def observe_ai_compute(self, duration_seconds: float):
        ...

    def inc_promo_generated(self):
        ...

    def inc_promo_duplicate_prevented(self):
        ...

    def inc_promo_generation_failure(self):
        ...

    def inc_telegram_notification(self, notification_type: str):
        ...

    def inc_telegram_notification_failure(self, notification_type: str):
        ...

    def observe_telegram_notification(self, duration_seconds: float):
        ...


@pytest.mark.anyio
async def test_start_command_triggers_welcome(tmp_path: Path) -> None:
    client = DummyClient()
    metrics = DummyMetrics()
    settings = Settings(FRONTEND_ORIGIN="https://example.com", TELEGRAM_ASSETS_DIR=str(tmp_path))
    (tmp_path / "welcome.png").write_bytes(b"placeholder")
    telegram_service = TelegramNotificationService(client=client, metrics=metrics, chat_ids=[], settings=settings)
    use_case = TelegramWebhookUseCase(telegram_service=telegram_service, settings=settings)

    await use_case.handle_update({"message": {"chat": {"id": 123}, "text": "/start"}})

    assert client.photos
    photo = client.photos[0]
    assert photo["chat_id"] == "123"
    assert "TicTacToe" in photo["caption"]
    assert photo["parse_mode"] == "HTML"
    assert photo["reply_markup"] is not None

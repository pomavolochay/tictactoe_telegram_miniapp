import pytest
from pathlib import Path

from tictactoe.application.services.telegram import TelegramNotificationService
from tictactoe.config import Settings


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def send_photo(self, *, chat_id: str, photo_path: str, caption: str, reply_markup=None, parse_mode: str = "HTML") -> None:
        self.calls.append({"chat_id": chat_id, "photo_path": photo_path, "caption": caption, "reply_markup": reply_markup, "parse_mode": parse_mode})


class FakeMetrics:
    def __init__(self) -> None:
        self.sent: list[str] = []
        self.failed: list[str] = []
        self.latencies: list[float] = []

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
        self.sent.append(notification_type)

    def inc_telegram_notification_failure(self, notification_type: str):
        self.failed.append(notification_type)

    def observe_telegram_notification(self, duration_seconds: float):
        self.latencies.append(duration_seconds)


@pytest.mark.anyio
async def test_notify_win_uses_win_asset_and_caption(tmp_path: Path):
    (tmp_path / "win.png").write_bytes(b"x")
    client = FakeClient()
    metrics = FakeMetrics()
    settings = Settings(TELEGRAM_ASSETS_DIR=str(tmp_path))
    service = TelegramNotificationService(client=client, metrics=metrics, chat_ids=[], settings=settings)
    await service.notify_win("ABC12", chat_id="42")
    assert client.calls
    call = client.calls[0]
    assert call["chat_id"] == "42"
    assert call["parse_mode"] == "HTML"
    assert "ABC12" in call["caption"]
    assert call["photo_path"].endswith("win.png")
    assert metrics.sent == ["win"]


@pytest.mark.anyio
async def test_notify_loss_uses_lose_asset(tmp_path: Path):
    (tmp_path / "lose.png").write_bytes(b"x")
    client = FakeClient()
    metrics = FakeMetrics()
    settings = Settings(TELEGRAM_ASSETS_DIR=str(tmp_path))
    service = TelegramNotificationService(client=client, metrics=metrics, chat_ids=[], settings=settings)
    await service.notify_loss(chat_id="55")
    call = client.calls[0]
    assert call["photo_path"].endswith("lose.png")
    assert metrics.sent == ["lose"]

import asyncio
import pytest

from tictactoe.application.use_cases import TelegramWebhookUseCase
from tictactoe.config import Settings


class DummyClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    async def send_message(self, *, chat_id: str, text: str, reply_markup=None) -> None:
        self.messages.append((chat_id, text))


@pytest.mark.anyio
async def test_start_command_triggers_welcome() -> None:
    client = DummyClient()
    settings = Settings(FRONTEND_ORIGIN="https://example.com")
    use_case = TelegramWebhookUseCase(client=client, settings=settings)
    await use_case.handle_update({
        "message": {
            "chat": {"id": 123},
            "text": "/start"
        }
    })
    assert client.messages
    chat_id, text = client.messages[0]
    assert chat_id == "123"
    assert "TicTacToe" in text or "Играть" in text

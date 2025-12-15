import json
from urllib.parse import urlencode

import pytest

from tictactoe.application.dtos import MoveCommand
from tictactoe.application.use_cases import MakeMoveUseCase
from tictactoe.domain.exceptions import InvalidMoveError
from tictactoe.domain.services.ai import MinimaxAIService
from tictactoe.infrastructure.metrics import MetricsAdapter


def build_init_data(user_id: int = 42) -> str:
    return urlencode({"user": json.dumps({"id": user_id, "username": "tester"})})


class StubPromoService:
    def __init__(self, code: str = "ABCDE") -> None:
        self.code = code
        self.calls = 0

    async def generate_unique_code(self) -> str:
        self.calls += 1
        return self.code


class StubTelegramService:
    def __init__(self) -> None:
        self.win_codes: list[str] = []
        self.losses = 0
        self.win_chat_ids: list[str | None] = []
        self.loss_chat_ids: list[str | None] = []

    async def notify_win(self, promo_code: str, chat_id: str | None = None) -> None:
        self.win_codes.append(promo_code)
        self.win_chat_ids.append(chat_id)

    async def notify_loss(self, chat_id: str | None = None) -> None:
        self.losses += 1
        self.loss_chat_ids.append(chat_id)


class TrackingMetrics(MetricsAdapter):
    def __init__(self) -> None:
        super().__init__()
        self.games_finished: list[str] = []
        self.moves: list[str] = []

    def inc_games_finished(self, result: str) -> None:
        self.games_finished.append(result)

    def inc_moves(self, actor: str) -> None:
        self.moves.append(actor)


@pytest.mark.anyio
async def test_make_move_player_win() -> None:
    promo = StubPromoService("S8A92")
    telegram = StubTelegramService()
    metrics = TrackingMetrics()
    use_case = MakeMoveUseCase(
        ai_service=MinimaxAIService(),
        promo_service=promo,
        telegram_service=telegram,
        metrics=metrics,
    )
    command = MoveCommand(
        board=["X", "X", "", "O", "O", "", "", "", ""],
        move_index=2,
        player_symbol="X",
        init_data=build_init_data(777),
    )
    result = await use_case.execute(command)
    assert result.status == "win"
    assert result.promo_code == "S8A92"
    assert telegram.win_codes == ["S8A92"]
    assert telegram.win_chat_ids == ["777"]
    assert result.next == "none"


@pytest.mark.anyio
async def test_make_move_draw() -> None:
    promo = StubPromoService()
    telegram = StubTelegramService()
    metrics = TrackingMetrics()
    use_case = MakeMoveUseCase(MinimaxAIService(), promo, telegram, metrics)
    result = await use_case.execute(
        MoveCommand(
            board=["X", "O", "X", "X", "O", "O", "O", "X", ""],
            move_index=8,
            player_symbol="X",
            init_data=build_init_data(),
        )
    )
    assert result.status == "draw"
    assert result.next == "none"
    assert telegram.losses == 0


@pytest.mark.anyio
async def test_make_move_loss_triggers_notification_with_chat_id() -> None:
    promo = StubPromoService()
    telegram = StubTelegramService()
    metrics = TrackingMetrics()
    use_case = MakeMoveUseCase(MinimaxAIService(), promo, telegram, metrics)
    result = await use_case.execute(
        MoveCommand(
            board=["X", "O", "X", "", "O", "", "", "", ""],
            move_index=3,
            player_symbol="X",
            init_data=build_init_data(555),
        )
    )
    assert result.status == "lose"
    assert telegram.losses == 1
    assert telegram.loss_chat_ids == ["555"]
    assert result.next == "none"


@pytest.mark.anyio
async def test_make_move_rejects_invalid_position() -> None:
    promo = StubPromoService()
    telegram = StubTelegramService()
    metrics = TrackingMetrics()
    use_case = MakeMoveUseCase(MinimaxAIService(), promo, telegram, metrics)
    command = MoveCommand(
        board=["X", "", "", "", "", "", "", "", ""],
        move_index=0,
        player_symbol="X",
        init_data=None,
    )
    with pytest.raises(InvalidMoveError):
        await use_case.execute(command)

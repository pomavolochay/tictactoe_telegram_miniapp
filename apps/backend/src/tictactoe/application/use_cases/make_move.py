from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import parse_qs

import structlog

from ...domain.entities.board import Board, GameStatus, PlayerSymbol
from ...domain.exceptions import GameAlreadyFinishedError, InvalidBoardError, InvalidMoveError
from ...domain.services.ai import MinimaxAIService
from ..dtos import GameStateDTO, MoveCommand
from ..interfaces import MetricsRecorder
from ..services import PromoCodeService, TelegramNotificationService

logger = structlog.get_logger()


@dataclass(slots=True)
class MakeMoveUseCase:
    ai_service: MinimaxAIService
    promo_service: PromoCodeService
    telegram_service: TelegramNotificationService
    metrics: MetricsRecorder
    ai_mistake_probability: float

    async def execute(self, command: MoveCommand) -> GameStateDTO:
        user_payload = self._parse_telegram_user(command.init_data)
        player_chat_id = command.chat_id or self._extract_chat_id(user_payload)
        if user_payload or player_chat_id:
            logger.info("telegram_user", payload=user_payload, chat_id=player_chat_id)

        board = self._load_board(command.board)
        if command.player_symbol != PlayerSymbol.X.value:
            self.metrics.inc_invalid_move("symbol")
            raise InvalidMoveError("Players must play as X")
        if board.is_finished():
            self.metrics.inc_invalid_move("finished")
            raise GameAlreadyFinishedError("Game already finished")

        if board.next_turn() is not PlayerSymbol.X:
            self.metrics.inc_invalid_move("turn_order")
            raise InvalidMoveError("It is not the player's turn")

        is_new_game = board.count(PlayerSymbol.X) == 0 and board.count(PlayerSymbol.O) == 0
        try:
            player_board = board.apply_move(command.move_index, PlayerSymbol.X)
        except InvalidMoveError:
            self.metrics.inc_invalid_move("illegal")
            raise
        if is_new_game:
            self.metrics.inc_games_started()
        self.metrics.inc_moves("player")

        player_winner = player_board.winner()
        if player_winner is PlayerSymbol.X:
            promo_code = await self.promo_service.generate_unique_code()
            await self.telegram_service.notify_win(promo_code, chat_id=player_chat_id)
            self.metrics.inc_games_finished(GameStatus.WIN.value)
            return GameStateDTO(
                board=player_board.serialize(),
                status=GameStatus.WIN.value,
                next="none",
                promo_code=promo_code,
            )

        if player_board.is_full():
            self.metrics.inc_games_finished(GameStatus.DRAW.value)
            return GameStateDTO(
                board=player_board.serialize(),
                status=GameStatus.DRAW.value,
                next="none",
            )

        ai_start = time.perf_counter()
        move_index = self._select_ai_move(player_board)
        duration = time.perf_counter() - ai_start
        self.metrics.observe_ai_compute(duration)

        updated_board = player_board.apply_move(move_index, PlayerSymbol.O)
        self.metrics.inc_moves("computer")

        winner = updated_board.winner()
        if winner is PlayerSymbol.O:
            await self.telegram_service.notify_loss(chat_id=player_chat_id)
            self.metrics.inc_games_finished(GameStatus.LOSE.value)
            return GameStateDTO(
                board=updated_board.serialize(),
                status=GameStatus.LOSE.value,
                next="none",
            )

        if updated_board.is_full():
            self.metrics.inc_games_finished(GameStatus.DRAW.value)
            return GameStateDTO(
                board=updated_board.serialize(),
                status=GameStatus.DRAW.value,
                next="none",
            )

        return GameStateDTO(
            board=updated_board.serialize(),
            status=GameStatus.IN_PROGRESS.value,
            next="player",
        )

    def _select_ai_move(self, board: Board) -> int:
        moves = board.available_moves()
        if not moves:
            return self.ai_service.pick_move(board)
        if random.random() < self.ai_mistake_probability:
            return random.choice(moves)
        return self.ai_service.pick_move(board)

    def _load_board(self, payload: list[str]) -> Board:
        try:
            return Board.from_sequence(payload)
        except InvalidBoardError:
            self.metrics.inc_invalid_move("board")
            raise

    def _parse_telegram_user(self, init_data: Optional[str]) -> dict[str, Any] | None:
        if not init_data:
            return None
        parsed = parse_qs(init_data)
        user_payload = parsed.get("user")
        if not user_payload:
            return None
        try:
            return json.loads(user_payload[0])
        except json.JSONDecodeError:
            logger.warning("telegram_user_parse_failed")
            return None

    def _extract_chat_id(self, user_payload: dict[str, Any] | None) -> str | None:
        if not user_payload:
            return None
        user_id = user_payload.get("id")
        if user_id is None:
            return None
        return str(user_id)

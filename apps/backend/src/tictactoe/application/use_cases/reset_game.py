from __future__ import annotations

from dataclasses import dataclass

from ...domain.entities.board import Board, GameStatus
from ..dtos import GameStateDTO


@dataclass(slots=True)
class ResetGameUseCase:
    def execute(self) -> GameStateDTO:
        board = Board.empty()
        return GameStateDTO(
            board=board.serialize(),
            status=GameStatus.IN_PROGRESS.value,
            next="player",
        )

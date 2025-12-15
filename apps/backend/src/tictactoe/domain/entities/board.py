from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Optional, Sequence, Tuple

from ..exceptions import GameAlreadyFinishedError, InvalidBoardError, InvalidMoveError

BoardState = Tuple[str, ...]


class PlayerSymbol(str, Enum):
    X = "X"
    O = "O"

    @property
    def opponent(self) -> "PlayerSymbol":
        return PlayerSymbol.O if self is PlayerSymbol.X else PlayerSymbol.X


class GameStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"


WINNING_COMBINATIONS: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


@dataclass(frozen=True)
class Board:
    cells: BoardState

    def __post_init__(self) -> None:
        if len(self.cells) != 9:
            raise InvalidBoardError("Board must contain 9 cells")
        for cell in self.cells:
            if cell not in {"", PlayerSymbol.X.value, PlayerSymbol.O.value}:
                raise InvalidBoardError("Board contains invalid symbols")

    @classmethod
    def empty(cls) -> "Board":
        return cls(tuple("" for _ in range(9)))

    def available_moves(self) -> List[int]:
        return [index for index, cell in enumerate(self.cells) if cell == ""]

    def count(self, symbol: PlayerSymbol) -> int:
        return sum(1 for cell in self.cells if cell == symbol.value)

    def winner(self) -> Optional[PlayerSymbol]:
        for combo in WINNING_COMBINATIONS:
            first, second, third = combo
            value = self.cells[first]
            if value and value == self.cells[second] == self.cells[third]:
                return PlayerSymbol(value)
        return None

    def is_full(self) -> bool:
        return all(cell != "" for cell in self.cells)

    def is_finished(self) -> bool:
        return self.winner() is not None or self.is_full()

    def next_turn(self) -> PlayerSymbol:
        x_count = self.count(PlayerSymbol.X)
        o_count = self.count(PlayerSymbol.O)
        if x_count == o_count:
            return PlayerSymbol.X
        if x_count == o_count + 1:
            return PlayerSymbol.O
        raise InvalidBoardError("Impossible turn order detected")

    def apply_move(self, index: int, symbol: PlayerSymbol) -> "Board":
        if self.is_finished():
            raise GameAlreadyFinishedError("Cannot move on finished board")
        if not 0 <= index < 9:
            raise InvalidMoveError("Move index out of range")
        if self.cells[index] != "":
            raise InvalidMoveError("Cell is already occupied")
        expected_turn = self.next_turn()
        if symbol is not expected_turn:
            raise InvalidMoveError("It's not this player's turn")
        updated = list(self.cells)
        updated[index] = symbol.value
        return Board(tuple(updated))

    def serialize(self) -> List[str]:
        return list(self.cells)

    @classmethod
    def from_sequence(cls, data: Sequence[str]) -> "Board":
        return cls(tuple(data))

    def __iter__(self) -> Iterable[str]:
        return iter(self.cells)

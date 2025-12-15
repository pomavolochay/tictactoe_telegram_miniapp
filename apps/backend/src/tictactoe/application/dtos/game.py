from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional


PlayerTurn = Literal["player", "computer", "none"]
GameStatusLiteral = Literal["in_progress", "win", "lose", "draw"]


@dataclass(slots=True)
class MoveCommand:
    board: List[str]
    move_index: int
    player_symbol: str
    init_data: Optional[str]
    chat_id: Optional[str]


@dataclass(slots=True)
class GameStateDTO:
    board: List[str]
    status: GameStatusLiteral
    next: PlayerTurn
    promo_code: Optional[str] = None

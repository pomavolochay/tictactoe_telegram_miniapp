from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

GameStatus = Literal["in_progress", "win", "lose", "draw"]
NextTurn = Literal["player", "computer", "none"]


class MoveRequest(BaseModel):
    board: list[Literal["X", "O", ""]] = Field(min_length=9, max_length=9)
    player_symbol: Literal["X"] = Field(alias="playerSymbol")
    move_index: int = Field(alias="moveIndex", ge=0, le=8)
    init_data: str | None = Field(default=None, alias="initData")
    chat_id: str | None = Field(default=None, alias="chatId")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "board": ["", "", "", "", "", "", "", "", ""],
                "playerSymbol": "X",
                "moveIndex": 4,
            }
        },
    }


class GameResponse(BaseModel):
    board: list[str]
    status: GameStatus
    next: NextTurn
    promo_code: str | None = Field(default=None, alias="promoCode")

    model_config = {"populate_by_name": True}


class ResetResponse(GameResponse):
    pass

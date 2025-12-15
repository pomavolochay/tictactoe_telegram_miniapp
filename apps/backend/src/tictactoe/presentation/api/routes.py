from __future__ import annotations

from fastapi import APIRouter, Depends, status

from ...application.dtos import GameStateDTO, MoveCommand
from ...application.use_cases import MakeMoveUseCase, ResetGameUseCase
from ...presentation.schemas.game import GameResponse, MoveRequest, ResetResponse
from ..dependencies import get_make_move_use_case, get_reset_game_use_case

router = APIRouter(prefix="/api/v1/game", tags=["game"])


@router.post("/move", response_model=GameResponse, status_code=status.HTTP_200_OK)
async def move(
    payload: MoveRequest,
    use_case: MakeMoveUseCase = Depends(get_make_move_use_case),
) -> GameResponse:
    dto = MoveCommand(
        board=payload.board,
        player_symbol=payload.player_symbol,
        move_index=payload.move_index,
        init_data=payload.init_data,
        chat_id=payload.chat_id,
    )
    result: GameStateDTO = await use_case.execute(dto)
    return GameResponse(
        board=result.board,
        status=result.status,
        next=result.next,
        promo_code=result.promo_code,
    )


@router.post("/reset", response_model=ResetResponse)
def reset(
    use_case: ResetGameUseCase = Depends(get_reset_game_use_case),
) -> ResetResponse:
    result = use_case.execute()
    return ResetResponse(board=result.board, status=result.status, next=result.next)

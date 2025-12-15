from tictactoe.domain.entities.board import Board
from tictactoe.domain.services.ai import MinimaxAIService


def test_ai_finishes_winning_column() -> None:
    board = Board.from_sequence(["X", "O", "", "X", "O", "", "", "", "X"])
    ai = MinimaxAIService()
    move = ai.pick_move(board)
    assert move == 7


def test_ai_blocks_immediate_player_win() -> None:
    board = Board.from_sequence(["X", "X", "", "", "O", "", "", "", ""])
    ai = MinimaxAIService()
    move = ai.pick_move(board)
    assert move == 2

import pytest

from tictactoe.domain.entities.board import Board, GameStatus, PlayerSymbol
from tictactoe.domain.exceptions import GameAlreadyFinishedError, InvalidBoardError, InvalidMoveError


def test_board_creation_and_winner_detection() -> None:
    board = Board.from_sequence(["X", "X", "X", "", "", "", "", "", ""])
    assert board.winner() == PlayerSymbol.X
    assert board.is_finished()


def test_board_available_moves() -> None:
    board = Board.from_sequence(["X", "O", "", "", "", "", "", "", ""])
    moves = board.available_moves()
    assert 2 in moves
    assert 0 not in moves


def test_invalid_board_length() -> None:
    with pytest.raises(InvalidBoardError):
        Board.from_sequence(["" for _ in range(8)])


def test_apply_move_enforces_turn_order() -> None:
    board = Board.empty()
    board = board.apply_move(0, PlayerSymbol.X)
    with pytest.raises(InvalidMoveError):
        board.apply_move(1, PlayerSymbol.X)


def test_apply_move_on_finished_board() -> None:
    board = Board.from_sequence(["X", "X", "X", "O", "O", "", "", "", ""])
    with pytest.raises(GameAlreadyFinishedError):
        board.apply_move(5, PlayerSymbol.O)

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from ..entities.board import Board, PlayerSymbol


@dataclass
class MinimaxAIService:
    computer_symbol: PlayerSymbol = PlayerSymbol.O

    def pick_move(self, board: Board) -> int:
        if board.is_finished():
            raise ValueError("Cannot pick a move for finished board")
        best_score = -math.inf
        best_move: Optional[int] = None
        alpha = -math.inf
        beta = math.inf
        for move in board.available_moves():
            child = board.apply_move(move, board.next_turn())
            score = self._minimax(child, alpha, beta)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
        if best_move is None:
            raise ValueError("No moves available to pick")
        return best_move

    def _minimax(self, board: Board, alpha: float, beta: float) -> float:
        winner = board.winner()
        if winner is not None:
            if winner == self.computer_symbol:
                return 1
            return -1
        if board.is_full():
            return 0

        is_computer_turn = board.next_turn() == self.computer_symbol
        if is_computer_turn:
            value = -math.inf
            for move in board.available_moves():
                child = board.apply_move(move, self.computer_symbol)
                value = max(value, self._minimax(child, alpha, beta))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value

        value = math.inf
        opponent = self.computer_symbol.opponent
        for move in board.available_moves():
            child = board.apply_move(move, opponent)
            value = min(value, self._minimax(child, alpha, beta))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

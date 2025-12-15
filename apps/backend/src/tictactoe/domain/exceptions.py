class DomainError(Exception):
    """Base class for domain-specific errors."""


class InvalidBoardError(DomainError):
    """Raised when client sends malformed board payload."""


class InvalidMoveError(DomainError):
    """Raised when a move cannot be applied to the board."""


class GameAlreadyFinishedError(DomainError):
    """Raised when a move is attempted although the game is finished."""

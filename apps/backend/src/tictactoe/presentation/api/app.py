from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from ...config import get_settings
from ...domain.exceptions import GameAlreadyFinishedError, InvalidBoardError, InvalidMoveError
from ...logging import configure_logging
from .routes import router as game_router
from .telegram import router as telegram_router
from ...infrastructure.metrics.http import MetricsMiddleware
import structlog


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(title="TicTacToe API", version="1.0.0")

    if settings.allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.add_middleware(MetricsMiddleware)
    app.include_router(game_router)
    app.include_router(telegram_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.mount("/metrics", make_asgi_app())

    register_exception_handlers(app)

    return app


def register_exception_handlers(app: FastAPI) -> None:
    logger = structlog.get_logger()

    @app.exception_handler(InvalidBoardError)
    async def invalid_board_handler(_: Request, exc: InvalidBoardError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(InvalidMoveError)
    async def invalid_move_handler(_: Request, exc: InvalidMoveError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(GameAlreadyFinishedError)
    async def finished_handler(_: Request, exc: GameAlreadyFinishedError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", error=str(exc))
        return JSONResponse(status_code=500, content={"detail": "internal_error"})

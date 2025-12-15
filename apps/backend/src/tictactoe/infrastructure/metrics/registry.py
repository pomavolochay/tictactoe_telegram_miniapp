from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from prometheus_client import Counter, Gauge, Histogram

HTTP_REQUESTS_TOTAL: Final = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=("method", "path", "status"),
)
HTTP_REQUEST_DURATION_SECONDS: Final = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    labelnames=("method", "path"),
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)
HTTP_IN_FLIGHT_REQUESTS: Final = Gauge(
    "http_in_flight_requests",
    "Number of HTTP requests currently in progress",
)

GAMES_STARTED_TOTAL: Final = Counter(
    "tictactoe_games_started_total",
    "Number of games started",
)
GAMES_FINISHED_TOTAL: Final = Counter(
    "tictactoe_games_finished_total",
    "Number of games finished",
    labelnames=("result",),
)
MOVES_TOTAL: Final = Counter(
    "tictactoe_moves_total",
    "Number of moves",
    labelnames=("actor",),
)
INVALID_MOVES_TOTAL: Final = Counter(
    "tictactoe_invalid_moves_total",
    "Invalid move attempts",
    labelnames=("reason",),
)
AI_COMPUTE_SECONDS: Final = Histogram(
    "tictactoe_ai_compute_seconds",
    "Time spent computing AI moves",
    buckets=(0.001, 0.01, 0.05, 0.1, 0.25, 0.5),
)
PROMO_GENERATED_TOTAL: Final = Counter(
    "promo_generated_total",
    "Number of promo codes generated",
)
PROMO_GENERATION_FAILURES_TOTAL: Final = Counter(
    "promo_generation_failures_total",
    "Promo code generation failures",
)
PROMO_DUPLICATES_PREVENTED_TOTAL: Final = Counter(
    "promo_duplicates_prevented_total",
    "Duplicate promo codes prevented",
)
TELEGRAM_NOTIFICATIONS_TOTAL: Final = Counter(
    "telegram_notifications_total",
    "Telegram notifications sent",
    labelnames=("type",),
)
TELEGRAM_NOTIFICATION_FAILURES_TOTAL: Final = Counter(
    "telegram_notification_failures_total",
    "Telegram notification failures",
)
TELEGRAM_NOTIFICATION_DURATION_SECONDS: Final = Histogram(
    "telegram_notification_duration_seconds",
    "Telegram notification duration",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2),
)


@dataclass(slots=True)
class MetricsAdapter:
    def inc_games_started(self) -> None:
        GAMES_STARTED_TOTAL.inc()

    def inc_games_finished(self, result: str) -> None:
        GAMES_FINISHED_TOTAL.labels(result=result).inc()

    def inc_moves(self, actor: str) -> None:
        MOVES_TOTAL.labels(actor=actor).inc()

    def inc_invalid_move(self, reason: str) -> None:
        INVALID_MOVES_TOTAL.labels(reason=reason).inc()

    def observe_ai_compute(self, duration_seconds: float) -> None:
        AI_COMPUTE_SECONDS.observe(duration_seconds)

    def inc_promo_generated(self) -> None:
        PROMO_GENERATED_TOTAL.inc()

    def inc_promo_generation_failure(self) -> None:
        PROMO_GENERATION_FAILURES_TOTAL.inc()

    def inc_promo_duplicate_prevented(self) -> None:
        PROMO_DUPLICATES_PREVENTED_TOTAL.inc()

    def inc_telegram_notification(self, notification_type: str) -> None:
        TELEGRAM_NOTIFICATIONS_TOTAL.labels(type=notification_type).inc()

    def inc_telegram_notification_failure(self) -> None:
        TELEGRAM_NOTIFICATION_FAILURES_TOTAL.inc()

    def observe_telegram_notification(self, duration_seconds: float) -> None:
        TELEGRAM_NOTIFICATION_DURATION_SECONDS.observe(duration_seconds)

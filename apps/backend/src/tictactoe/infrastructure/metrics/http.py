from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from . import HTTP_IN_FLIGHT_REQUESTS, HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION_SECONDS


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, exclude_paths: set[str] | None = None) -> None:
        super().__init__(app)
        self._exclude_paths = exclude_paths or {"/metrics", "/health"}

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        path = request.url.path
        method = request.method
        is_excluded = path in self._exclude_paths
        if not is_excluded:
            HTTP_IN_FLIGHT_REQUESTS.inc()
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.perf_counter() - start
            if not is_excluded:
                HTTP_IN_FLIGHT_REQUESTS.dec()
                HTTP_REQUESTS_TOTAL.labels(method=method, path=self._normalize(path), status=str(status_code)).inc()
                HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=self._normalize(path)).observe(duration)

    def _normalize(self, path: str) -> str:
        if path.startswith("/api/v1/game"):
            return "/api/v1/game"
        return path

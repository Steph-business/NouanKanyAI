"""Middleware ASGI journalisant le statut et la durée des requêtes HTTP."""

import logging
import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("nouankany.http")


class RequestLoggingMiddleware:
    """Journalise la méthode, le chemin, le statut et le temps de traitement."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        started = time.perf_counter()
        status_code = 500

        async def capture_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            await send(message)

        try:
            await self.app(scope, receive, capture_status)
        finally:
            duration_ms = (time.perf_counter() - started) * 1000
            logger.info(
                "http_request method=%s path=%s status=%s duration_ms=%.2f",
                scope.get("method", ""),
                scope.get("path", ""),
                status_code,
                duration_ms,
            )

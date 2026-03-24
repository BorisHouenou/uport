"""Audit logging middleware — records every mutating API call."""
import time
import uuid
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

SKIP_PATHS = {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in SKIP_PATHS:
            return await call_next(request)

        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        with structlog.contextvars.bound_contextvars(request_id=request_id):
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)

            if request.method in ("POST", "PUT", "PATCH", "DELETE"):
                logger.info(
                    "api_request",
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                )

        response.headers["X-Request-ID"] = request_id
        return response

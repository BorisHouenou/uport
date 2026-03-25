"""Audit logging middleware — records every mutating API call to the audit_events table."""
import time
import uuid
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

SKIP_PATHS = {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}
MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in SKIP_PATHS:
            return await call_next(request)

        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        with structlog.contextvars.bound_contextvars(request_id=request_id):
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)

            if request.method in MUTATING_METHODS:
                logger.info(
                    "api_request",
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                )

                # Persist to audit_events table (best-effort — never blocks response)
                try:
                    from core.database import AsyncSessionLocal as async_session_factory
                    org_id = _extract_org_id(request)
                    actor_id = _extract_actor(request)
                    ip = _extract_ip(request)

                    async with async_session_factory() as db:
                        await db.execute(
                            text("""
                                INSERT INTO audit_events
                                    (id, org_id, entity_type, entity_id, action,
                                     actor_id, ip_address, payload, created_at)
                                VALUES
                                    (:id, :org_id, :entity_type, :entity_id, :action,
                                     :actor_id, :ip, :payload, now())
                            """),
                            {
                                "id": str(uuid.uuid4()),
                                "org_id": org_id,
                                "entity_type": _path_to_entity(request.url.path),
                                "entity_id": None,
                                "action": f"{request.method}:{request.url.path}",
                                "actor_id": actor_id,
                                "ip": ip,
                                "payload": f'{{"status":{response.status_code},"duration_ms":{duration_ms}}}',
                            },
                        )
                        await db.commit()
                except Exception:
                    # Never let audit persistence crash the request
                    logger.warning("audit_persist_failed", path=request.url.path)

        response.headers["X-Request-ID"] = request_id
        return response


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _extract_org_id(request: Request) -> str | None:
    """Pull org_id from Clerk JWT state if available."""
    try:
        state = request.state
        return str(getattr(state, "org_id", None))
    except Exception:
        return None


def _extract_actor(request: Request) -> str | None:
    try:
        return getattr(request.state, "user_id", None)
    except Exception:
        return None


def _extract_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _path_to_entity(path: str) -> str:
    """Map /api/v1/certificates/... → 'certificate'."""
    segments = [s for s in path.split("/") if s and s not in ("api", "v1")]
    return segments[0].rstrip("s") if segments else "unknown"

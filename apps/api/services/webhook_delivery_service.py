"""
Outbound webhook delivery service.

Sends HMAC-SHA256 signed HTTP POST requests to registered endpoints.
Delivery is best-effort with up to 3 retries (0s, 5s, 30s back-off).
Events are fired in a background asyncio task — never blocks the caller.
"""
import asyncio
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from models.webhook import WebhookEndpoint

logger = structlog.get_logger()

_RETRY_DELAYS = [0, 5, 30]  # seconds between attempts
_TIMEOUT = 10  # seconds per HTTP request


async def fire_event(
    org_id: uuid.UUID,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    """
    Non-blocking: schedules delivery to all active endpoints subscribed to event_type.
    Safe to call from any async context (request handler, Celery task via asyncio.run).
    """
    asyncio.create_task(_deliver_to_all(org_id, event_type, payload))


async def fire_event_sync(
    org_id: uuid.UUID,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    """Blocking variant for use in Celery workers (call via asyncio.run)."""
    await _deliver_to_all(org_id, event_type, payload)


# ─── Internal ─────────────────────────────────────────────────────────────────

async def _deliver_to_all(org_id: uuid.UUID, event_type: str, payload: dict) -> None:
    async with AsyncSessionLocal() as db:
        endpoints = await _get_subscribed_endpoints(db, org_id, event_type)

    if not endpoints:
        return

    event_id = str(uuid.uuid4())
    timestamp = int(time.time())
    body = json.dumps({
        "id": event_id,
        "type": event_type,
        "created": timestamp,
        "data": payload,
    }, default=str)

    await asyncio.gather(*[
        _deliver_with_retry(ep, body, event_type, event_id)
        for ep in endpoints
    ])


async def _get_subscribed_endpoints(
    db: AsyncSession, org_id: uuid.UUID, event_type: str
) -> list[WebhookEndpoint]:
    result = await db.execute(
        select(WebhookEndpoint)
        .where(WebhookEndpoint.org_id == org_id)
        .where(WebhookEndpoint.active.is_(True))
    )
    return [ep for ep in result.scalars().all() if _subscribes(ep, event_type)]


def _subscribes(ep: WebhookEndpoint, event_type: str) -> bool:
    """Check if endpoint is subscribed to event_type (supports wildcard '*')."""
    return "*" in ep.events or event_type in ep.events


async def _deliver_with_retry(
    ep: WebhookEndpoint, body: str, event_type: str, event_id: str
) -> None:
    for attempt, delay in enumerate(_RETRY_DELAYS):
        if delay:
            await asyncio.sleep(delay)
        try:
            sig = _sign(ep.secret, body)
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.post(
                    ep.url,
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-Uportai-Event": event_type,
                        "X-Uportai-Delivery": event_id,
                        "X-Uportai-Signature-256": f"sha256={sig}",
                        "X-Uportai-Timestamp": str(int(time.time())),
                    },
                )
            if resp.status_code < 300:
                logger.info("webhook_delivered", endpoint=str(ep.id), event=event_type, attempt=attempt + 1)
                return
            logger.warning("webhook_non_2xx", endpoint=str(ep.id), status=resp.status_code, attempt=attempt + 1)
        except Exception as exc:
            logger.warning("webhook_error", endpoint=str(ep.id), error=str(exc), attempt=attempt + 1)

    logger.error("webhook_failed_all_retries", endpoint=str(ep.id), event=event_type)


def _sign(secret: str, body: str) -> str:
    return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()

"""Outbound webhook endpoint management (register, list, delete)."""
import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from models.webhook import WebhookEndpoint

router = APIRouter(prefix="/webhooks/endpoints", tags=["webhooks"])

SUPPORTED_EVENTS = {"certificate.issued", "declaration.expired", "compliance.alert", "*"}


class EndpointCreate(BaseModel):
    url: HttpUrl
    events: list[str]
    description: str | None = None


class EndpointResponse(BaseModel):
    id: uuid.UUID
    url: str
    events: list[str]
    active: bool
    description: str | None
    created_at: str

    model_config = {"from_attributes": True}


@router.post("", status_code=201)
async def register_endpoint(
    payload: EndpointCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Register a new webhook endpoint for this organisation."""
    unknown = set(payload.events) - SUPPORTED_EVENTS
    if unknown:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported event types: {sorted(unknown)}. Valid: {sorted(SUPPORTED_EVENTS)}",
        )

    org_id = uuid.UUID(current_user["org_id"])
    secret = secrets.token_hex(32)
    ep = WebhookEndpoint(
        org_id=org_id,
        url=str(payload.url),
        secret=secret,
        events=payload.events,
        description=payload.description,
    )
    db.add(ep)
    await db.commit()
    await db.refresh(ep)

    return {
        "id": str(ep.id),
        "url": ep.url,
        "events": ep.events,
        "active": ep.active,
        "description": ep.description,
        "secret": secret,  # Only returned on creation — store it now
        "created_at": ep.created_at.isoformat(),
    }


@router.get("")
async def list_endpoints(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all registered webhook endpoints for this organisation."""
    org_id = uuid.UUID(current_user["org_id"])
    result = await db.execute(
        select(WebhookEndpoint)
        .where(WebhookEndpoint.org_id == org_id)
        .order_by(WebhookEndpoint.created_at.desc())
    )
    eps = result.scalars().all()
    return [
        {
            "id": str(ep.id),
            "url": ep.url,
            "events": ep.events,
            "active": ep.active,
            "description": ep.description,
            "created_at": ep.created_at.isoformat(),
        }
        for ep in eps
    ]


@router.patch("/{endpoint_id}")
async def toggle_endpoint(
    endpoint_id: uuid.UUID,
    active: bool,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Enable or disable a webhook endpoint."""
    ep = await _get_ep(db, endpoint_id, current_user["org_id"])
    ep.active = active
    await db.commit()
    return {"id": str(ep.id), "active": ep.active}


@router.delete("/{endpoint_id}", status_code=204)
async def delete_endpoint(
    endpoint_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Delete a webhook endpoint."""
    ep = await _get_ep(db, endpoint_id, current_user["org_id"])
    await db.delete(ep)
    await db.commit()


async def _get_ep(db: AsyncSession, endpoint_id: uuid.UUID, org_id_str: str) -> WebhookEndpoint:
    org_id = uuid.UUID(org_id_str)
    result = await db.execute(
        select(WebhookEndpoint)
        .where(WebhookEndpoint.id == endpoint_id)
        .where(WebhookEndpoint.org_id == org_id)
    )
    ep = result.scalar_one_or_none()
    if not ep:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found")
    return ep

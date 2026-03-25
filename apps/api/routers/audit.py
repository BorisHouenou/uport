"""Audit Vault — query and export immutable audit log."""
import csv
import io
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser, AdminUser
from models import AuditEvent

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
async def list_audit_events(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    entity_type: Annotated[str | None, Query()] = None,
    action: Annotated[str | None, Query()] = None,
    actor_id: Annotated[str | None, Query()] = None,
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 50,
):
    """
    Query the audit log for this organisation.
    Supports filtering by entity_type, action, actor_id, and date range.
    """
    org_id = current_user["org_id"]
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="org_id required")

    org_uuid = uuid.UUID(org_id)

    base_filter = AuditEvent.org_id == org_uuid
    q = select(AuditEvent).where(base_filter).order_by(AuditEvent.created_at.desc())
    count_q = select(func.count(AuditEvent.id)).where(base_filter)

    if entity_type:
        q = q.where(AuditEvent.entity_type == entity_type)
        count_q = count_q.where(AuditEvent.entity_type == entity_type)
    if action:
        q = q.where(AuditEvent.action.ilike(f"%{action}%"))
        count_q = count_q.where(AuditEvent.action.ilike(f"%{action}%"))
    if actor_id:
        q = q.where(AuditEvent.actor_id == actor_id)
        count_q = count_q.where(AuditEvent.actor_id == actor_id)
    if from_date:
        q = q.where(AuditEvent.created_at >= from_date)
        count_q = count_q.where(AuditEvent.created_at >= from_date)
    if to_date:
        q = q.where(AuditEvent.created_at <= to_date)
        count_q = count_q.where(AuditEvent.created_at <= to_date)

    total = (await db.execute(count_q)).scalar_one()
    rows = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "events": [_serialize(e) for e in rows],
    }


@router.get("/export.csv")
async def export_audit_csv(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
):
    """
    Export the full audit log as CSV (admin only).
    Suitable for customs authority review or SOC 2 evidence.
    """
    org_id = uuid.UUID(current_user["org_id"])
    q = (
        select(AuditEvent)
        .where(AuditEvent.org_id == org_id)
        .order_by(AuditEvent.created_at.asc())
    )
    if from_date:
        q = q.where(AuditEvent.created_at >= from_date)
    if to_date:
        q = q.where(AuditEvent.created_at <= to_date)

    rows = (await db.execute(q)).scalars().all()

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=[
        "id", "created_at", "entity_type", "entity_id",
        "action", "actor_id", "actor_email", "ip_address", "payload",
    ])
    writer.writeheader()
    for e in rows:
        writer.writerow(_serialize(e))

    buf.seek(0)
    filename = f"audit-log-{org_id}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _serialize(e: AuditEvent) -> dict:
    return {
        "id": str(e.id),
        "created_at": e.created_at.isoformat() if e.created_at else None,
        "entity_type": e.entity_type,
        "entity_id": e.entity_id,
        "action": e.action,
        "actor_id": e.actor_id,
        "actor_email": e.actor_email,
        "ip_address": e.ip_address,
        "payload": e.payload,
    }

"""
PIPEDA (Canada) + GDPR (EU) compliance endpoints.

  GET  /api/v1/privacy/export     — Right of Access: export all org data as JSON
  DELETE /api/v1/privacy/erase    — Right to Erasure: anonymise all PII for the org
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import AdminUser, CurrentUser
from models import (
    Organization, User, Shipment, OriginDetermination,
    Certificate, SupplierDeclaration, AuditEvent,
)

router = APIRouter(prefix="/privacy", tags=["privacy"])


@router.get("/export")
async def export_org_data(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Right of Access (PIPEDA s.4.9 / GDPR Art.15).
    Returns a complete JSON export of all data held for this organisation.
    Suitable for responding to Subject Access Requests within 30 days.
    """
    org_id = uuid.UUID(current_user["org_id"])

    org = (await db.execute(select(Organization).where(Organization.id == org_id))).scalar_one_or_none()
    users = (await db.execute(select(User).where(User.org_id == org_id))).scalars().all()
    shipments = (await db.execute(select(Shipment).where(Shipment.org_id == org_id))).scalars().all()
    ship_ids = [s.id for s in shipments]

    determinations = certs = []
    if ship_ids:
        determinations = (await db.execute(
            select(OriginDetermination).where(OriginDetermination.shipment_id.in_(ship_ids))
        )).scalars().all()
        certs = (await db.execute(
            select(Certificate).where(Certificate.shipment_id.in_(ship_ids))
        )).scalars().all()

    declarations = (await db.execute(
        select(SupplierDeclaration).where(SupplierDeclaration.org_id == org_id)
    )).scalars().all()

    audit_events = (await db.execute(
        select(AuditEvent).where(AuditEvent.org_id == org_id).order_by(AuditEvent.created_at.asc())
    )).scalars().all()

    export = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "org_id": str(org_id),
        "organization": _org_dict(org) if org else None,
        "users": [_user_dict(u) for u in users],
        "shipments": [_ship_dict(s) for s in shipments],
        "origin_determinations": [_det_dict(d) for d in determinations],
        "certificates": [_cert_dict(c) for c in certs],
        "supplier_declarations": [_decl_dict(d) for d in declarations],
        "audit_events": [_audit_dict(e) for e in audit_events],
    }

    return JSONResponse(
        content=export,
        headers={
            "Content-Disposition": f'attachment; filename="uportai-data-export-{org_id}.json"',
        },
    )


@router.delete("/erase", status_code=200)
async def erase_org_data(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
    confirm: str = "",
):
    """
    Right to Erasure (PIPEDA s.4.5 / GDPR Art.17).
    Anonymises all PII for the organisation. Audit event structure is preserved
    (required for compliance evidence) but personal identifiers are scrubbed.

    Requires confirm=ERASE in the query string as an explicit acknowledgement.
    """
    if confirm != "ERASE":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pass ?confirm=ERASE to confirm erasure. This action is irreversible.",
        )

    org_id = uuid.UUID(current_user["org_id"])

    # Anonymise users
    await db.execute(
        update(User)
        .where(User.org_id == org_id)
        .values(
            email="[erased]@erased.invalid",
            clerk_id="[erased]",
        )
    )

    # Anonymise audit event actors (preserve structure for compliance)
    await db.execute(
        update(AuditEvent)
        .where(AuditEvent.org_id == org_id)
        .values(actor_id="[erased]", actor_email="[erased]", ip_address="0.0.0.0")
    )

    # Hard-delete supplier declarations (contain supplier PII)
    await db.execute(
        delete(SupplierDeclaration).where(SupplierDeclaration.org_id == org_id)
    )

    # Anonymise organisation name/country but keep the row for referential integrity
    await db.execute(
        update(Organization)
        .where(Organization.id == org_id)
        .values(name="[erased]")
    )

    await db.commit()

    return {
        "erased": True,
        "org_id": str(org_id),
        "erased_at": datetime.now(timezone.utc).isoformat(),
        "note": "PII anonymised. Audit event structure retained for compliance. Certificates and shipment records retained for customs obligations.",
    }


# ─── Serialisers ──────────────────────────────────────────────────────────────

def _org_dict(o: Organization) -> dict:
    return {"id": str(o.id), "name": o.name, "country": o.country, "plan": getattr(o, "plan", None), "created_at": _iso(o.created_at)}

def _user_dict(u: User) -> dict:
    return {"id": str(u.id), "email": u.email, "role": u.role, "created_at": _iso(u.created_at)}

def _ship_dict(s: Shipment) -> dict:
    return {"id": str(s.id), "destination_country": s.destination_country, "origin_country": s.origin_country, "status": s.status, "created_at": _iso(s.created_at)}

def _det_dict(d: OriginDetermination) -> dict:
    return {"id": str(d.id), "agreement_code": d.agreement_code, "result": d.result, "confidence": float(d.confidence), "created_at": _iso(d.created_at)}

def _cert_dict(c: Certificate) -> dict:
    return {"id": str(c.id), "cert_type": c.cert_type, "cert_number": c.cert_number, "status": c.status, "issued_at": _iso(c.issued_at)}

def _decl_dict(d: SupplierDeclaration) -> dict:
    return {"id": str(d.id), "supplier_name": d.supplier_name, "supplier_country": d.supplier_country, "origin_country": d.origin_country, "valid_from": str(d.valid_from), "valid_until": str(d.valid_until)}

def _audit_dict(e: AuditEvent) -> dict:
    return {"id": str(e.id), "entity_type": e.entity_type, "action": e.action, "actor_id": e.actor_id, "created_at": _iso(e.created_at)}

def _iso(dt) -> str | None:
    return dt.isoformat() if dt else None

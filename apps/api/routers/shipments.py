"""Shipment management endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from models.shipment import Shipment
from models.product import Product

router = APIRouter(prefix="/shipments", tags=["shipments"])


class ShipmentCreate(BaseModel):
    product_id: str
    destination_country: str
    origin_country: str
    shipment_value_usd: float | None = None
    reference_number: str | None = None
    notes: str | None = None


class ShipmentResponse(BaseModel):
    id: str
    product_id: str | None
    destination_country: str
    origin_country: str
    status: str
    shipment_value_usd: float | None
    reference_number: str | None

    model_config = {"from_attributes": True}


@router.post("", response_model=ShipmentResponse, status_code=201)
async def create_shipment(
    payload: ShipmentCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=403, detail="No organization associated with this account")

    # Verify product belongs to org
    product = (await db.execute(
        select(Product).where(
            Product.id == uuid.UUID(payload.product_id),
            Product.org_id == uuid.UUID(org_id),
        )
    )).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    shipment = Shipment(
        id=uuid.uuid4(),
        org_id=uuid.UUID(org_id),
        product_id=uuid.UUID(payload.product_id),
        destination_country=payload.destination_country,
        origin_country=payload.origin_country or product.origin_country or "CA",
        shipment_value_usd=payload.shipment_value_usd,
        reference_number=payload.reference_number,
        notes=payload.notes,
        status="pending",
    )
    db.add(shipment)
    await db.commit()
    await db.refresh(shipment)
    return _serialize(shipment)


@router.get("", response_model=list[ShipmentResponse])
async def list_shipments(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=403, detail="No organization associated with this account")

    rows = (await db.execute(
        select(Shipment)
        .where(Shipment.org_id == uuid.UUID(org_id))
        .order_by(Shipment.created_at.desc())
        .limit(100)
    )).scalars().all()
    return [_serialize(s) for s in rows]


def _serialize(s: Shipment) -> dict:
    return {
        "id": str(s.id),
        "product_id": str(s.product_id) if s.product_id else None,
        "destination_country": s.destination_country,
        "origin_country": s.origin_country,
        "status": s.status,
        "shipment_value_usd": float(s.shipment_value_usd) if s.shipment_value_usd is not None else None,
        "reference_number": s.reference_number,
    }

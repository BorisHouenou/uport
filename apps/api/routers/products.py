"""Product management endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from models.product import Product

router = APIRouter(prefix="/products", tags=["products"])


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    hs_code: str | None = None
    origin_country: str | None = None
    sku: str | None = None
    unit_cost_usd: float | None = None


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str | None
    hs_code: str | None
    hs_description: str | None
    hs_confidence: float | None
    origin_country: str | None
    sku: str | None
    unit_cost_usd: float | None

    model_config = {"from_attributes": True}


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    payload: ProductCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(
            status_code=403, detail="No organization associated with this account"
        )

    product = Product(
        id=uuid.uuid4(),
        org_id=uuid.UUID(org_id),
        name=payload.name,
        description=payload.description,
        hs_code=payload.hs_code,
        origin_country=payload.origin_country,
        sku=payload.sku,
        unit_cost_usd=payload.unit_cost_usd,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return _serialize(product)


@router.get("", response_model=list[ProductResponse])
async def list_products(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(
            status_code=403, detail="No organization associated with this account"
        )

    rows = (
        (
            await db.execute(
                select(Product)
                .where(Product.org_id == uuid.UUID(org_id))
                .order_by(Product.created_at.desc())
                .limit(100)
            )
        )
        .scalars()
        .all()
    )
    return [_serialize(p) for p in rows]


def _serialize(p: Product) -> dict:
    return {
        "id": str(p.id),
        "name": p.name,
        "description": p.description,
        "hs_code": p.hs_code,
        "hs_description": p.hs_description,
        "hs_confidence": float(p.hs_confidence)
        if p.hs_confidence is not None
        else None,
        "origin_country": p.origin_country,
        "sku": p.sku,
        "unit_cost_usd": float(p.unit_cost_usd)
        if p.unit_cost_usd is not None
        else None,
    }

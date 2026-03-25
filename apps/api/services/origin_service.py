"""Origin determination DB service layer."""
import uuid
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import OriginDetermination, Shipment, BOMItem, Product

logger = structlog.get_logger()


async def get_determination_by_id(
    db: AsyncSession,
    determination_id: uuid.UUID,
    org_id: uuid.UUID,
) -> dict | None:
    # Join through shipment to enforce org_id isolation
    result = await db.execute(
        select(OriginDetermination)
        .join(Shipment, OriginDetermination.shipment_id == Shipment.id)
        .where(OriginDetermination.id == determination_id)
        .where(Shipment.org_id == org_id)
    )
    det = result.scalar_one_or_none()
    return det


async def list_org_determinations(
    db: AsyncSession,
    org_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    offset = (page - 1) * page_size
    result = await db.execute(
        select(OriginDetermination)
        .join(Shipment, OriginDetermination.shipment_id == Shipment.id)
        .where(Shipment.org_id == org_id)
        .order_by(OriginDetermination.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = result.scalars().all()
    return {"determinations": items, "page": page, "page_size": page_size}


# ─── Sync versions for Celery tasks ───────────────────────────────────────────

def get_shipment_data_sync(shipment_id: str, org_id: str) -> dict | None:
    """Synchronous DB read for Celery workers."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from core.config import get_settings
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        ship = session.execute(
            select(Shipment)
            .where(Shipment.id == uuid.UUID(shipment_id))
            .where(Shipment.org_id == uuid.UUID(org_id))
        ).scalar_one_or_none()
        if not ship:
            return None
        # Get product + BOM
        product = session.execute(
            select(Product).where(Product.id == ship.product_id)
        ).scalar_one_or_none() if ship.product_id else None

        bom_items = []
        if product:
            items = session.execute(
                select(BOMItem).where(BOMItem.product_id == product.id)
            ).scalars().all()
            bom_items = [
                {
                    "description": item.description,
                    "hs_code": item.hs_code,
                    "origin_country": item.origin_country,
                    "quantity": float(item.quantity),
                    "unit_cost": float(item.unit_cost),
                    "currency": item.currency,
                    "is_originating": item.is_originating,
                }
                for item in items
            ]

        return {
            "hs_code": product.hs_code if product else "0000.00",
            "product_description": product.name if product else "Unknown",
            "origin_country": ship.origin_country,
            "destination_country": ship.destination_country,
            "shipment_value_usd": float(ship.shipment_value_usd or 0),
            "bom": bom_items,
        }


def save_determination_sync(shipment_id: str, org_id: str, result: Any) -> None:
    """Persist origin determination results to DB (sync, for Celery)."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from core.config import get_settings
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        for det_dict in result.determinations:
            det = OriginDetermination(
                id=uuid.uuid4(),
                shipment_id=uuid.UUID(shipment_id),
                agreement_code=det_dict["agreement_code"],
                agreement_name=det_dict.get("agreement_code", "").upper(),
                rule_applied=det_dict["rule_applied"],
                rule_text=det_dict.get("rule_text", ""),
                result=det_dict["result"],
                confidence=det_dict["confidence"],
                reasoning=det_dict.get("reasoning", ""),
                raw_llm_response=det_dict,
                status="completed",
            )
            session.add(det)
        session.commit()

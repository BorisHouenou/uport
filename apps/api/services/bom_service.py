"""BOM DB service layer."""
import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import BOMItem, Product

logger = structlog.get_logger()


async def get_bom_items(
    db: AsyncSession,
    product_id: uuid.UUID,
    org_id: uuid.UUID,
) -> dict:
    # Verify product belongs to org
    product = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .where(Product.org_id == org_id)
    )
    product = product.scalar_one_or_none()
    if not product:
        return {"product_id": product_id, "items": [], "total_items": 0, "total_cost_usd": 0.0}

    items_result = await db.execute(
        select(BOMItem).where(BOMItem.product_id == product_id)
    )
    items = items_result.scalars().all()
    total_cost = sum(float(i.unit_cost) * float(i.quantity) for i in items)

    non_orig = sum(float(i.unit_cost) * float(i.quantity) for i in items if i.is_originating is False)
    foreign_pct = round((non_orig / total_cost * 100) if total_cost > 0 else 0, 2)

    return {
        "product_id": product_id,
        "items": items,
        "total_items": len(items),
        "total_cost_usd": round(total_cost, 2),
        "foreign_content_pct": foreign_pct,
    }


def save_bom_items_sync(product_id: str, org_id: str, items: list[dict]) -> None:
    """Persist BOM items after upload+classification (sync for Celery)."""
    from sqlalchemy import create_engine, delete
    from sqlalchemy.orm import Session
    from core.config import get_settings
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        # Replace existing BOM items for this product
        session.execute(delete(BOMItem).where(BOMItem.product_id == uuid.UUID(product_id)))
        for item in items:
            bom = BOMItem(
                id=uuid.uuid4(),
                product_id=uuid.UUID(product_id),
                description=item["description"],
                quantity=item["quantity"],
                unit_cost=item["unit_cost"],
                currency=item.get("currency", "USD"),
                origin_country=item.get("origin_country", "XX"),
                hs_code=item.get("hs_code"),
                hs_confidence=item.get("hs_confidence"),
                classified_by=item.get("classified_by", "ai"),
            )
            session.add(bom)
        session.commit()

"""Bill of Materials upload and management endpoints."""

import asyncio
import logging
import os
import sys
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db, AsyncSessionLocal
from middleware.auth import CurrentUser
from models import BOMItem, Product
from schemas.bom import BOMUploadResponse, BOMItemList

router = APIRouter(prefix="/bom", tags=["bom"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}
MAX_FILE_SIZE_MB = 10

_AI_AGENTS = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "packages", "ai-agents")
)
if _AI_AGENTS not in sys.path:
    sys.path.insert(0, _AI_AGENTS)


async def _classify_and_update(product_id: uuid.UUID, item_ids: list[uuid.UUID], descriptions: list[str]) -> None:
    """Background task: classify HS codes and write results back to DB."""
    try:
        from hs_classifier import classify_batch
        batch_input = [{"description": d} for d in descriptions]
        results = await asyncio.to_thread(classify_batch, batch_input)
    except Exception as exc:
        logger.warning("HS batch classification failed for product %s: %s", product_id, exc)
        return

    async with AsyncSessionLocal() as db:
        for item_id, result in zip(item_ids, results):
            if result.confidence >= 0.5 and result.hs_code and result.hs_code != "0000.00":
                await db.execute(
                    update(BOMItem)
                    .where(BOMItem.id == item_id)
                    .values(
                        hs_code=result.hs_code,
                        hs_confidence=result.confidence,
                        classified_by="ai",
                    )
                )
        await db.commit()
    logger.info("HS classification complete for product %s: %d items", product_id, len(item_ids))


@router.post("/upload", response_model=BOMUploadResponse, status_code=201)
async def upload_bom(
    product_id: uuid.UUID,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a Bill of Materials file (CSV, Excel, JSON).
    Saves items immediately, then classifies HS codes in the background.
    Returns 201 with status="processing"; frontend polls until hs_code is set.
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit",
        )

    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=403, detail="No organization associated with this account")

    product = (
        await db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.org_id == uuid.UUID(org_id),
            )
        )
    ).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        from bom_parser import parse_bom
        rows = parse_bom(content, ext)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse BOM file: {exc}",
        ) from exc

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No valid rows found. Check the file has a 'description' column.",
        )

    # ── Persist immediately (replace existing BOM) ─────────────────────────────
    await db.execute(delete(BOMItem).where(BOMItem.product_id == product_id))

    saved_items: list[tuple[uuid.UUID, str]] = []  # (id, description) for items needing HS
    for row in rows:
        item_id = uuid.uuid4()
        classified_by = "imported" if row.hs_code else "ai"
        db.add(BOMItem(
            id=item_id,
            product_id=product_id,
            description=row.description,
            quantity=row.quantity,
            unit_cost=row.unit_cost,
            currency=row.currency,
            origin_country=row.origin_country,
            hs_code=row.hs_code,
            hs_confidence=None,
            classified_by=classified_by,
        ))
        if not row.hs_code and row.description:
            saved_items.append((item_id, row.description))

    await db.commit()

    # ── Schedule background classification for items without HS codes ──────────
    if saved_items:
        ids, descs = zip(*saved_items)
        background_tasks.add_task(_classify_and_update, product_id, list(ids), list(descs))

    return BOMUploadResponse(
        task_id=str(uuid.uuid4()),
        status="processing" if saved_items else "completed",
        product_id=product_id,
    )


@router.get("/{product_id}/items", response_model=BOMItemList)
async def get_bom_items(
    product_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return all BOM line items for a product with their classified HS codes."""
    from services.bom_service import get_bom_items

    return await get_bom_items(db, product_id, current_user["org_id"])

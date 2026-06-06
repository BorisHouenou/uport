"""Bill of Materials upload and management endpoints."""

import os
import sys
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from models import BOMItem, Product
from schemas.bom import BOMUploadResponse, BOMItemList

router = APIRouter(prefix="/bom", tags=["bom"])

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}
MAX_FILE_SIZE_MB = 10

# Add ai-agents package to path once at import time
_AI_AGENTS = os.path.join(os.path.dirname(__file__), "..", "..", "..", "packages", "ai-agents")
if _AI_AGENTS not in sys.path:
    sys.path.insert(0, _AI_AGENTS)


@router.post("/upload", response_model=BOMUploadResponse, status_code=201)
async def upload_bom(
    product_id: uuid.UUID,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a Bill of Materials file (CSV, Excel, JSON).
    Parses and AI-classifies HS codes inline; returns immediately after saving.
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

    from sqlalchemy import select
    org_id = current_user["org_id"]
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

    # ── Parse ─────────────────────────────────────────────────────────────────
    from bom_parser import parse_bom
    rows = parse_bom(content, ext)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No valid rows found in BOM file. Check that it has a 'description' column.",
        )

    # ── Batch-classify items missing HS codes (single Claude call) ────────────
    unclassified_idx = [i for i, r in enumerate(rows) if not r.hs_code and r.description]
    if unclassified_idx:
        from hs_classifier import classify_batch
        batch_input = [{"description": rows[i].description} for i in unclassified_idx]
        batch_results = classify_batch(batch_input)
        for list_pos, row_idx in enumerate(unclassified_idx):
            result = batch_results[list_pos]
            if result.confidence >= 0.5:
                rows[row_idx].hs_code = result.hs_code

    # ── Persist (replace existing BOM for this product) ───────────────────────
    await db.execute(delete(BOMItem).where(BOMItem.product_id == product_id))

    batch_results_map: dict[int, float] = {}
    if unclassified_idx:
        for list_pos, row_idx in enumerate(unclassified_idx):
            r = batch_results[list_pos]  # type: ignore[possibly-undefined]
            if r.confidence >= 0.5:
                batch_results_map[row_idx] = r.confidence

    for i, row in enumerate(rows):
        hs_confidence = batch_results_map.get(i) if i in batch_results_map else None
        classified_by = (
            "ai" if i in batch_results_map
            else ("imported" if row.hs_code else "manual")
        )
        db.add(BOMItem(
            id=uuid.uuid4(),
            product_id=product_id,
            description=row.description,
            quantity=row.quantity,
            unit_cost=row.unit_cost,
            currency=row.currency,
            origin_country=row.origin_country,
            hs_code=row.hs_code,
            hs_confidence=hs_confidence,
            classified_by=classified_by,
        ))

    await db.commit()

    return BOMUploadResponse(
        task_id=str(uuid.uuid4()),
        status="completed",
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

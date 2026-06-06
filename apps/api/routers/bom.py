"""Bill of Materials upload and management endpoints."""

import logging
import os
import sys
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from models import BOMItem, Product
from schemas.bom import BOMUploadResponse, BOMItemList

router = APIRouter(prefix="/bom", tags=["bom"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}
MAX_FILE_SIZE_MB = 10

# Packages are on PYTHONPATH in production (Dockerfile sets it).
# Add the local path as fallback for dev.
_AI_AGENTS = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "packages", "ai-agents")
)
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
    Parses inline, AI-classifies missing HS codes in a single batch call,
    then saves. Returns after commit with status="completed".
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

    # Verify product belongs to this org
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

    # ── Parse ─────────────────────────────────────────────────────────────────
    from bom_parser import parse_bom
    rows = parse_bom(content, ext)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No valid rows found. Check the file has a 'description' column.",
        )

    # ── Batch-classify items missing HS codes (one Claude call for all) ───────
    # Map: row index → (hs_code, confidence) for items we classified
    ai_results: dict[int, tuple[str, float]] = {}

    unclassified = [(i, r) for i, r in enumerate(rows) if not r.hs_code and r.description]
    if unclassified:
        try:
            from hs_classifier import classify_batch
            batch_results = classify_batch([{"description": r.description} for _, r in unclassified])
            for (row_idx, _), result in zip(unclassified, batch_results):
                if result.confidence >= 0.5:
                    rows[row_idx].hs_code = result.hs_code
                    ai_results[row_idx] = (result.hs_code, result.confidence)
        except Exception as exc:
            # Classification is best-effort — save without HS codes rather than fail the upload
            logger.warning("HS batch classification failed, saving without codes: %s", exc)

    # ── Persist (replace existing BOM for this product) ───────────────────────
    await db.execute(delete(BOMItem).where(BOMItem.product_id == product_id))

    for i, row in enumerate(rows):
        hs_confidence: float | None = None
        classified_by = "manual"

        if i in ai_results:
            hs_confidence = ai_results[i][1]
            classified_by = "ai"
        elif row.hs_code:
            classified_by = "imported"

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

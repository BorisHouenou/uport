"""Bill of Materials upload and management endpoints."""
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from schemas.bom import BOMUploadResponse, BOMItemList

router = APIRouter(prefix="/bom", tags=["bom"])

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}
MAX_FILE_SIZE_MB = 10


@router.post("/upload", response_model=BOMUploadResponse, status_code=201)
async def upload_bom(
    product_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a Bill of Materials file (CSV, Excel, JSON).
    Triggers async parsing and HS code classification per line item.
    """
    import os
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
    from services.tasks.bom_tasks import process_bom_upload
    task = process_bom_upload.delay(
        org_id=current_user["org_id"],
        product_id=str(product_id),
        file_content=content.hex(),
        file_ext=ext,
    )
    return BOMUploadResponse(task_id=task.id, status="processing", product_id=product_id)


@router.get("/{product_id}/items", response_model=BOMItemList)
async def get_bom_items(
    product_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return all BOM line items for a product with their classified HS codes."""
    from services.bom_service import get_bom_items
    return await get_bom_items(db, product_id, current_user["org_id"])

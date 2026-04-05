"""Supplier declaration management endpoints."""
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from schemas.suppliers import (
    SupplierDeclarationCreate,
    SupplierDeclarationResponse,
    SupplierDeclarationList,
)

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.post("/declarations", response_model=SupplierDeclarationResponse, status_code=201)
async def submit_declaration(
    payload: SupplierDeclarationCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Submit or update a supplier origin declaration for a product."""
    from services.supplier_service import upsert_declaration
    return await upsert_declaration(db, payload, current_user["org_id"])


@router.post("/declarations/{declaration_id}/upload-doc")
async def upload_supporting_document(
    declaration_id: uuid.UUID,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Attach a supporting document (e.g., supplier cert) to a declaration."""
    from services.supplier_service import attach_document
    url = await attach_document(db, declaration_id, file, current_user["org_id"])
    return {"document_url": url}


@router.get("/declarations", response_model=SupplierDeclarationList)
async def list_declarations(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    expiring_within_days: int | None = None,
):
    """
    List supplier declarations. Pass expiring_within_days to filter
    declarations approaching expiry (useful for renewal workflows).
    """
    from services.supplier_service import list_declarations
    return await list_declarations(db, current_user["org_id"], expiring_within_days)


@router.get("/declarations/{declaration_id}", response_model=SupplierDeclarationResponse)
async def get_declaration(
    declaration_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    from services.supplier_service import get_declaration_by_id
    result = await get_declaration_by_id(db, declaration_id, current_user["org_id"])
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Declaration not found")
    return result

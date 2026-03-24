"""Origin determination endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from schemas.origin import (
    OriginDeterminationCreate,
    OriginDeterminationResponse,
    OriginQueryRequest,
    OriginQueryResponse,
)

router = APIRouter(prefix="/origin", tags=["origin"])


@router.post("/determine", response_model=OriginDeterminationResponse, status_code=201)
async def determine_origin(
    payload: OriginDeterminationCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Run the RoO determination engine for a shipment.
    Evaluates all applicable trade agreements and returns pass/fail
    per agreement with full reasoning chain.
    """
    # Dispatched to Celery for async processing in Sprint 3
    from services.tasks.ai_tasks import run_origin_determination
    task = run_origin_determination.delay(
        org_id=current_user["org_id"],
        shipment_id=str(payload.shipment_id),
        agreement_codes=payload.agreement_codes,
    )
    return OriginDeterminationResponse(
        task_id=task.id,
        status="queued",
        shipment_id=payload.shipment_id,
    )


@router.get("/{determination_id}", response_model=OriginQueryResponse)
async def get_determination(
    determination_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a completed origin determination with full reasoning."""
    from services.origin_service import get_determination_by_id
    result = await get_determination_by_id(db, determination_id, current_user["org_id"])
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Determination not found")
    return result

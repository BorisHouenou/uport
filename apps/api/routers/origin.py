"""Origin determination endpoints."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from models import OriginDetermination, Shipment, HumanCorrection
from schemas.origin import (
    OriginDeterminationCreate,
    OriginDeterminationResponse,
    OriginQueryRequest,
    OriginQueryResponse,
)

router = APIRouter(prefix="/origin", tags=["origin"])

CONFIDENCE_REVIEW_THRESHOLD = 0.75


class ReviewDecision(BaseModel):
    decision: str  # "approved" | "rejected"
    reviewer_notes: str | None = None
    corrected_result: str | None = None  # override result if rejected


class CorrectionCreate(BaseModel):
    corrected_hs_code: str | None = None
    corrected_result: str | None = None
    corrected_rule: str | None = None
    reviewer_notes: str | None = None


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


@router.get("/review-queue")
async def get_review_queue(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """
    Return determinations flagged for human review — those below the
    confidence threshold or explicitly marked needs_human_review.
    """
    org_id = current_user["org_id"]
    q = (
        select(OriginDetermination)
        .join(Shipment, OriginDetermination.shipment_id == Shipment.id)
        .where(Shipment.org_id == org_id)
        .where(
            (OriginDetermination.confidence < CONFIDENCE_REVIEW_THRESHOLD) |
            (OriginDetermination.status == "needs_review")
        )
        .where(OriginDetermination.status != "reviewed")
        .order_by(OriginDetermination.confidence.asc())  # lowest confidence first
    )
    from sqlalchemy import func
    total_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(total_q)).scalar_one()
    rows = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_serialize_det(d) for d in rows],
    }


@router.post("/{determination_id}/review")
async def submit_review(
    determination_id: uuid.UUID,
    payload: ReviewDecision,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a human review decision on a flagged determination.
    Approved: confirms the AI result. Rejected: overrides the result.
    """
    if payload.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=422, detail="decision must be 'approved' or 'rejected'")

    org_id = current_user["org_id"]
    result = await db.execute(
        select(OriginDetermination)
        .join(Shipment, OriginDetermination.shipment_id == Shipment.id)
        .where(OriginDetermination.id == determination_id)
        .where(Shipment.org_id == org_id)
    )
    det = result.scalar_one_or_none()
    if not det:
        raise HTTPException(status_code=404, detail="Determination not found")

    det.status = "reviewed"
    det.reviewed_by = current_user.get("email") or current_user.get("user_id")
    if payload.decision == "rejected" and payload.corrected_result:
        det.result = payload.corrected_result
    if payload.reviewer_notes:
        det.reasoning = (det.reasoning or "") + f"\n\n[Review note — {det.reviewed_by}]: {payload.reviewer_notes}"

    await db.commit()
    return {"id": str(det.id), "status": det.status, "result": det.result}


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


@router.post("/{determination_id}/correction", status_code=201)
async def submit_correction(
    determination_id: uuid.UUID,
    payload: CorrectionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Store a human correction on a determination for the fine-tuning pipeline.
    Corrections are exported weekly as JSONL to S3 for model improvement.
    """
    org_id = uuid.UUID(current_user["org_id"])
    result = await db.execute(
        select(OriginDetermination)
        .join(Shipment, OriginDetermination.shipment_id == Shipment.id)
        .where(OriginDetermination.id == determination_id)
        .where(Shipment.org_id == org_id)
    )
    det = result.scalar_one_or_none()
    if not det:
        raise HTTPException(status_code=404, detail="Determination not found")

    correction = HumanCorrection(
        org_id=org_id,
        determination_id=determination_id,
        original_result=det.result,
        corrected_result=payload.corrected_result,
        original_rule=det.rule_applied,
        corrected_rule=payload.corrected_rule,
        agreement_code=det.agreement_code,
        reviewer_id=current_user.get("user_id"),
        reviewer_notes=payload.reviewer_notes,
    )
    db.add(correction)
    await db.commit()
    await db.refresh(correction)
    return {"correction_id": str(correction.id), "determination_id": str(determination_id)}


def _serialize_det(d: OriginDetermination) -> dict:
    return {
        "id": str(d.id),
        "shipment_id": str(d.shipment_id),
        "agreement_code": d.agreement_code,
        "agreement_name": d.agreement_name,
        "rule_applied": d.rule_applied,
        "result": d.result,
        "confidence": float(d.confidence),
        "reasoning": d.reasoning,
        "preferential_rate": d.preferential_rate,
        "mfn_rate": d.mfn_rate,
        "status": d.status,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }

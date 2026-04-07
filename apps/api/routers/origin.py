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
    org_id = current_user["org_id"]
    shipment_id = payload.shipment_id

    # Verify the shipment exists and belongs to this org
    if not org_id:
        raise HTTPException(status_code=403, detail="No organization associated with this account")
    ship_result = await db.execute(
        select(Shipment).where(
            Shipment.id == shipment_id,
            Shipment.org_id == uuid.UUID(org_id),
        )
    )
    shipment = ship_result.scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Try Celery first; fall back to inline sync execution
    task_id = str(uuid.uuid4())
    try:
        from services.tasks.ai_tasks import run_origin_determination
        task = run_origin_determination.delay(
            org_id=org_id,
            shipment_id=str(shipment_id),
            agreement_codes=payload.agreement_codes,
        )
        task_id = task.id
        return OriginDeterminationResponse(
            task_id=task_id,
            status="queued",
            shipment_id=shipment_id,
        )
    except Exception:
        pass  # Celery unavailable — run inline below

    # ── Inline determination (no Celery worker required) ──────────────────────
    from models import Product, BOMItem

    product = None
    if shipment.product_id:
        p = await db.execute(select(Product).where(Product.id == shipment.product_id))
        product = p.scalar_one_or_none()

    bom_rows = []
    if product:
        b = await db.execute(select(BOMItem).where(BOMItem.product_id == product.id))
        bom_rows = b.scalars().all()

    agreement_codes = payload.agreement_codes or ["cusma"]
    _AGREEMENT_NAMES = {
        "cusma": "Canada-United States-Mexico Agreement",
        "ceta": "Canada-European Union Comprehensive Economic and Trade Agreement",
        "cptpp": "Comprehensive and Progressive Agreement for Trans-Pacific Partnership",
        "ckfta": "Canada-Korea Free Trade Agreement",
    }

    determinations = []
    for code in agreement_codes:
        total_cost = sum(float(b.unit_cost) * float(b.quantity) for b in bom_rows) or 1.0
        ca_cost = sum(
            float(b.unit_cost) * float(b.quantity)
            for b in bom_rows if b.origin_country == "CA"
        )
        rvc = (ca_cost / total_cost) * 100 if total_cost else 0
        passes = rvc >= 35  # simplified RVC threshold

        det = OriginDetermination(
            id=uuid.uuid4(),
            shipment_id=shipment_id,
            agreement_code=code,
            agreement_name=_AGREEMENT_NAMES.get(code, code.upper()),
            rule_applied="rvc_build_down",
            rule_text=f"Regional Value Content (Build-Down) ≥ 35% — calculated RVC: {rvc:.1f}%",
            result="pass" if passes else "fail",
            confidence=0.88 if passes else 0.72,
            reasoning=(
                f"Product: {product.name if product else 'Unknown'} (HS {product.hs_code if product else 'N/A'}). "
                f"Origin: {shipment.origin_country} → Destination: {shipment.destination_country}. "
                f"BOM analysis: {len(bom_rows)} components, CA-originating cost ${ca_cost:.2f} of ${total_cost:.2f} total "
                f"= {rvc:.1f}% RVC. {'Qualifies' if passes else 'Does not qualify'} under {code.upper()}."
            ),
            preferential_rate="0%" if passes else None,
            mfn_rate="6.5%",
            savings_per_unit=float(shipment.shipment_value_usd or 0) * 0.065 if passes else 0,
            status="completed",
        )
        db.add(det)
        determinations.append(det)

    await db.commit()

    best = next((d for d in determinations if d.result == "pass"), None)
    total_savings = sum(d.savings_per_unit or 0 for d in determinations if d.result == "pass")

    return OriginDeterminationResponse(
        task_id=str(determinations[0].id),  # real ID so GET /origin/{id} resolves
        status="completed",
        shipment_id=shipment_id,
        results=[
            {
                "agreement_code": d.agreement_code,
                "agreement_name": d.agreement_name,
                "rule_applied": d.rule_applied,
                "rule_text": d.rule_text,
                "result": d.result,
                "confidence": float(d.confidence),
                "reasoning": d.reasoning,
                "preferential_rate": d.preferential_rate,
                "mfn_rate": d.mfn_rate,
                "savings_per_unit": float(d.savings_per_unit or 0),
            }
            for d in determinations
        ],
        best_agreement=best.agreement_code if best else None,
        total_savings_usd=total_savings,
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
    """Retrieve all determinations for the shipment associated with this determination ID."""
    org_id = current_user["org_id"]

    # Look up the anchor determination to get shipment_id
    anchor = await db.execute(
        select(OriginDetermination)
        .join(Shipment, OriginDetermination.shipment_id == Shipment.id)
        .where(OriginDetermination.id == determination_id)
        .where(Shipment.org_id == uuid.UUID(org_id))
    )
    det = anchor.scalar_one_or_none()
    if not det:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Determination not found")

    # Fetch ALL determinations for this shipment
    all_dets_result = await db.execute(
        select(OriginDetermination)
        .where(OriginDetermination.shipment_id == det.shipment_id)
        .order_by(OriginDetermination.created_at.asc())
    )
    all_dets = all_dets_result.scalars().all()

    best = next((d for d in all_dets if d.result == "pass"), None)
    total_savings = sum(float(d.savings_per_unit or 0) for d in all_dets if d.result == "pass")

    return {
        "id": str(det.id),
        "shipment_id": str(det.shipment_id),
        "status": "completed",
        "results": [
            {
                "agreement_code": d.agreement_code,
                "agreement_name": d.agreement_name,
                "rule_applied": d.rule_applied,
                "rule_text": d.rule_text or "",
                "result": d.result,
                "confidence": float(d.confidence),
                "reasoning": d.reasoning or "",
                "preferential_rate": d.preferential_rate,
                "mfn_rate": d.mfn_rate,
                "savings_per_unit": float(d.savings_per_unit or 0),
            }
            for d in all_dets
        ],
        "best_agreement": best.agreement_code if best else None,
        "total_savings_usd": total_savings,
        "reviewed_by": det.reviewed_by,
    }


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

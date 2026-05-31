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

    task_id = str(uuid.uuid4())

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

    # ── Run the real origin determination engine ──────────────────────────────
    import sys as _sys
    import os as _os
    _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), "..", "..", "..", "packages", "ai-agents"))

    from origin_agent import ShipmentInput, run_origin_determination

    bom_dicts = [
        {
            "description": b.description,
            "hs_code": b.hs_code,
            "origin_country": b.origin_country,
            "unit_cost": float(b.unit_cost),
            "quantity": float(b.quantity),
            "currency": b.currency,
            "is_originating": b.is_originating,
        }
        for b in bom_rows
    ]

    ship_input = ShipmentInput(
        hs_code=product.hs_code if product else "0000",
        product_description=product.name if product else "Unknown product",
        production_country=shipment.origin_country,
        destination_country=shipment.destination_country,
        transaction_value_usd=float(shipment.shipment_value_usd or 0),
        bom=bom_dicts,
        agreement_codes=payload.agreement_codes or [],
    )

    engine_result = run_origin_determination(ship_input)

    _AGREEMENT_NAMES = {
        "cusma": "Canada-United States-Mexico Agreement",
        "ceta": "Canada-European Union Comprehensive Economic and Trade Agreement",
        "cptpp": "Comprehensive and Progressive Agreement for Trans-Pacific Partnership",
        "afcfta": "African Continental Free Trade Area",
        "ckfta": "Canada-Korea Free Trade Agreement",
        "ccofta": "Canada-Colombia Free Trade Agreement",
        "cpafta": "Canada-Panama Free Trade Agreement",
        "cifta": "Canada-Israel Free Trade Agreement",
        "cufta": "Canada-Ukraine Free Trade Agreement",
        "cjfta": "Canada-Jordan Free Trade Agreement",
    }

    determinations = []
    for det_dict in engine_result.determinations:
        code = det_dict.get("agreement_code", "")
        passing = det_dict.get("result") == "pass"
        saving = det_dict.get("savings_per_unit") or (
            float(shipment.shipment_value_usd or 0) * 0.065 if passing else 0
        )
        det = OriginDetermination(
            id=uuid.uuid4(),
            shipment_id=shipment_id,
            agreement_code=code,
            agreement_name=_AGREEMENT_NAMES.get(code, code.upper()),
            rule_applied=det_dict.get("rule_applied", "unknown"),
            rule_text=det_dict.get("rule_text", ""),
            result=det_dict.get("result", "fail"),
            confidence=float(det_dict.get("confidence", 0.0)),
            reasoning=det_dict.get("reasoning", ""),
            preferential_rate="0%" if passing else None,
            mfn_rate=None,
            savings_per_unit=saving,
            status="completed" if not engine_result.needs_human_review else "needs_review",
        )
        db.add(det)
        determinations.append(det)

    # If engine returned no determinations (no FTA / no rules), persist a stub
    if not determinations:
        stub = OriginDetermination(
            id=uuid.uuid4(),
            shipment_id=shipment_id,
            agreement_code="none",
            agreement_name="No applicable agreement",
            rule_applied="none",
            rule_text="; ".join(engine_result.review_reasons),
            result="fail",
            confidence=0.0,
            reasoning=engine_result.llm_summary or "No applicable FTA found.",
            status="needs_review",
        )
        db.add(stub)
        determinations.append(stub)

    await db.commit()

    best = next((d for d in determinations if d.result == "pass"), None)
    total_savings = sum(float(d.savings_per_unit or 0) for d in determinations if d.result == "pass")

    return OriginDeterminationResponse(
        task_id=str(determinations[0].id),
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

    # Fetch ALL determinations for this shipment, deduplicated to latest per agreement
    all_dets_result = await db.execute(
        select(OriginDetermination)
        .where(OriginDetermination.shipment_id == det.shipment_id)
        .order_by(OriginDetermination.agreement_code, OriginDetermination.created_at.desc())
    )
    all_rows = all_dets_result.scalars().all()
    # Keep only the most recent determination per agreement code
    seen: set[str] = set()
    all_dets = []
    for d in all_rows:
        if d.agreement_code not in seen:
            seen.add(d.agreement_code)
            all_dets.append(d)

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

    # Pull shipment context for richer calibration data
    ship_result = await db.execute(
        select(Shipment).where(Shipment.id == det.shipment_id)
    )
    ship = ship_result.scalar_one_or_none()

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
        hs_chapter=payload.corrected_hs_code[:2] if payload.corrected_hs_code else None,
        origin_country=ship.origin_country if ship else None,
        destination_country=ship.destination_country if ship else None,
        confidence_at_review=float(det.confidence) if det.confidence is not None else None,
    )
    db.add(correction)
    await db.commit()
    await db.refresh(correction)
    return {"correction_id": str(correction.id), "determination_id": str(determination_id)}


@router.get("/calibration")
async def get_calibration_stats(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Return the most recent confidence calibration stats.

    Shows per-agreement accuracy derived from human corrections:
    how often the AI determination matched the expert reviewer.
    Refreshed daily by the compute_calibration_stats Celery task.
    """
    from sqlalchemy import text
    row = await db.execute(
        text("""
            SELECT computed_at, stats
            FROM calibration_stats
            ORDER BY computed_at DESC
            LIMIT 1
        """)
    )
    result = row.fetchone()

    if not result:
        # First run — compute inline from corrections
        corr_row = await db.execute(
            text("""
                SELECT
                    agreement_code,
                    COUNT(*) AS total,
                    SUM(CASE WHEN corrected_result IS NOT DISTINCT FROM original_result THEN 1 ELSE 0 END) AS confirmed,
                    AVG(CASE WHEN corrected_result IS NOT DISTINCT FROM original_result THEN 1.0 ELSE 0.0 END) AS accuracy
                FROM human_corrections
                GROUP BY agreement_code
            """)
        )
        rows = corr_row.fetchall()
        if not rows:
            return {
                "computed_at": None,
                "message": "No corrections recorded yet — accuracy calibration starts after first human reviews",
                "agreements": {},
                "total_corrections": 0,
            }
        stats = {
            r[0] or "unknown": {
                "total_reviews": int(r[1]),
                "confirmed": int(r[2]),
                "accuracy_90d": round(float(r[3] or 0), 4),
            }
            for r in rows
        }
        return {"computed_at": None, "agreements": stats, "total_corrections": sum(v["total_reviews"] for v in stats.values())}

    return {
        "computed_at": result[0].isoformat() if result[0] else None,
        "agreements": result[1],
        "total_corrections": sum(
            v.get("total_reviews", 0) for v in result[1].values()
        ) if result[1] else 0,
    }


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

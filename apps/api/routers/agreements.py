"""Trade agreement and RoO rules reference data endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from schemas.agreements import AgreementList, RooRuleList, HSCodeClassification

router = APIRouter(prefix="/agreements", tags=["agreements"])


@router.get("/", response_model=AgreementList)
async def list_agreements(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    origin_country: str | None = Query(None, description="ISO-3166 alpha-2 country code"),
    destination_country: str | None = Query(None),
):
    """List all trade agreements, optionally filtered by origin/destination country pair."""
    from services.agreement_service import get_applicable_agreements
    return await get_applicable_agreements(db, origin_country, destination_country)


@router.get("/{agreement_code}/rules", response_model=RooRuleList)
async def get_roo_rules(
    agreement_code: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    hs_code: str | None = Query(None, description="HS code (4 or 6 digit)"),
):
    """Retrieve Rules of Origin for a specific agreement, optionally filtered by HS code."""
    from services.agreement_service import get_rules_for_agreement
    return await get_rules_for_agreement(db, agreement_code, hs_code)


@router.post("/classify-hs", response_model=HSCodeClassification)
async def classify_hs_code(
    description: str = Query(..., description="Product description for AI classification"),
    current_user: CurrentUser = Depends(),
):
    """
    AI-powered HS code classification from a product description.
    Returns primary HS code, confidence score, and alternative classifications.
    """
    from services.tasks.ai_tasks import classify_hs_code_task
    task = classify_hs_code_task.delay(description=description, org_id=current_user["org_id"])
    return HSCodeClassification(task_id=task.id, status="classifying", description=description)

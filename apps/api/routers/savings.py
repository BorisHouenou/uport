"""Savings / ROI summary endpoints."""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from services.savings_service import get_savings_summary

router = APIRouter(prefix="/savings", tags=["savings"])


@router.get("/summary")
async def savings_summary(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return tariff savings KPIs, monthly trend, and breakdown by agreement."""
    org_id = uuid.UUID(current_user["org_id"])
    return await get_savings_summary(db, org_id)

"""Stripe billing endpoints: checkout, portal, subscription info."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    tier: str          # starter | growth | enterprise
    success_url: str
    cancel_url: str


class PortalRequest(BaseModel):
    return_url: str


@router.post("/checkout")
async def create_checkout(
    body: CheckoutRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return a Stripe Checkout URL for the selected tier."""
    from services.billing_service import create_checkout_session

    try:
        url = await create_checkout_session(
            org_id=current_user["org_id"],
            user_email=current_user.get("email", ""),
            tier=body.tier,
            success_url=body.success_url,
            cancel_url=body.cancel_url,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"url": url}


@router.post("/portal")
async def customer_portal(
    body: PortalRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return a Stripe Customer Portal URL to manage subscription."""
    from sqlalchemy import select
    from models.organization import Organization
    from services.billing_service import create_portal_session

    result = await db.execute(
        select(Organization).where(Organization.id == current_user["org_id"])
    )
    org = result.scalar_one_or_none()
    if not org or not org.stripe_customer_id:
        raise HTTPException(status_code=404, detail="No Stripe customer found for this org")

    url = await create_portal_session(org.stripe_customer_id, body.return_url)
    return {"url": url}


@router.get("/subscription")
async def subscription_info(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return the current subscription tier, status, and limits."""
    from services.billing_service import get_subscription_info
    return await get_subscription_info(current_user["org_id"], db)


@router.get("/usage")
async def certificate_usage(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return current month certificate usage vs. plan included count."""
    from services.billing_service import get_certificate_usage
    return await get_certificate_usage(current_user["org_id"], db)

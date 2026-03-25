"""Incoming webhook handlers (Stripe, Clerk)."""
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from core.config import get_settings
from core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="stripe-signature"),
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe subscription lifecycle events."""
    import stripe as stripe_lib
    from core.security import verify_stripe_webhook
    from services.billing_service import (
        handle_checkout_completed,
        handle_subscription_updated,
        handle_subscription_deleted,
        handle_invoice_payment_failed,
    )

    payload = await request.body()
    event = verify_stripe_webhook(payload, stripe_signature)

    event_type = event["type"]
    event_data = event["data"]

    if event_type == "checkout.session.completed":
        await handle_checkout_completed(event_data, db)
    elif event_type in ("customer.subscription.updated", "customer.subscription.trial_will_end"):
        await handle_subscription_updated(event_data, db)
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(event_data, db)
    elif event_type == "invoice.payment_failed":
        await handle_invoice_payment_failed(event_data, db)

    return {"received": True}


@router.post("/clerk")
async def clerk_webhook(request: Request):
    """Handle Clerk user/org lifecycle events (user.created, org.created, etc.)."""
    from services.auth_service import handle_clerk_event
    payload = await request.json()
    await handle_clerk_event(payload)
    return {"received": True}

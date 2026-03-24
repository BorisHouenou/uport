"""Incoming webhook handlers (Stripe, Clerk)."""
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from core.config import get_settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="stripe-signature"),
):
    """Handle Stripe subscription lifecycle events."""
    from core.security import verify_stripe_webhook
    from services.billing_service import handle_stripe_event

    payload = await request.body()
    event = verify_stripe_webhook(payload, stripe_signature)
    await handle_stripe_event(event)
    return {"received": True}


@router.post("/clerk")
async def clerk_webhook(request: Request):
    """Handle Clerk user/org lifecycle events (user.created, org.created, etc.)."""
    from services.auth_service import handle_clerk_event
    payload = await request.json()
    await handle_clerk_event(payload)
    return {"received": True}

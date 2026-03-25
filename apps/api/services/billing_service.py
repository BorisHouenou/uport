"""
Stripe billing service.

Subscription tiers:
  starter   — $149/mo  — 25 shipments/mo,  3 users
  growth    — $499/mo  — 100 shipments/mo, 10 users, API access
  enterprise— $1499/mo — unlimited,        SSO, dedicated support
"""
from __future__ import annotations

import os
from typing import Any

import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from core.config import get_settings
from models.organization import Organization

stripe.api_key = get_settings().stripe_secret_key

# ──────────────────────────────────────────────
# Price IDs (set in environment / Stripe dashboard)
# ──────────────────────────────────────────────
PRICE_IDS: dict[str, str] = {
    "starter":    os.getenv("STRIPE_PRICE_STARTER",    "price_starter_placeholder"),
    "growth":     os.getenv("STRIPE_PRICE_GROWTH",     "price_growth_placeholder"),
    "enterprise": os.getenv("STRIPE_PRICE_ENTERPRISE", "price_enterprise_placeholder"),
}

# Metered overage price — charged per certificate above plan limit
# Set STRIPE_PRICE_CERT_OVERAGE in Stripe dashboard (metered, $2/unit)
PRICE_CERT_OVERAGE: str = os.getenv("STRIPE_PRICE_CERT_OVERAGE", "price_cert_overage_placeholder")

# Included certificates per tier per month (matches certificates_limit in Organization)
CERT_INCLUDED: dict[str, int] = {
    "starter": 10,
    "growth": 50,
    "enterprise": -1,  # unlimited
}

TIER_LIMITS: dict[str, dict[str, Any]] = {
    "starter":    {"shipments_per_month": 25,  "users": 3,   "api_access": False},
    "growth":     {"shipments_per_month": 100, "users": 10,  "api_access": True},
    "enterprise": {"shipments_per_month": -1,  "users": -1,  "api_access": True},
}


# ──────────────────────────────────────────────
# Checkout session
# ──────────────────────────────────────────────

async def create_checkout_session(
    org_id: str,
    user_email: str,
    tier: str,
    success_url: str,
    cancel_url: str,
) -> str:
    """Create a Stripe Checkout session and return the hosted URL."""
    if tier not in PRICE_IDS:
        raise ValueError(f"Unknown tier: {tier}")

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": PRICE_IDS[tier], "quantity": 1}],
        customer_email=user_email,
        client_reference_id=org_id,
        metadata={"org_id": org_id, "tier": tier},
        success_url=success_url,
        cancel_url=cancel_url,
        subscription_data={"metadata": {"org_id": org_id, "tier": tier}},
    )
    return session.url


# ──────────────────────────────────────────────
# Customer portal (manage subscription)
# ──────────────────────────────────────────────

async def create_portal_session(stripe_customer_id: str, return_url: str) -> str:
    session = stripe.billing_portal.Session.create(
        customer=stripe_customer_id,
        return_url=return_url,
    )
    return session.url


# ──────────────────────────────────────────────
# Webhook event handlers
# ──────────────────────────────────────────────

async def handle_checkout_completed(event_data: dict, db: AsyncSession) -> None:
    """Persist Stripe customer + subscription after first checkout."""
    session = event_data["object"]
    org_id = session.get("client_reference_id") or session["metadata"].get("org_id")
    if not org_id:
        return

    subscription_id = session.get("subscription")
    customer_id = session.get("customer")
    tier = session["metadata"].get("tier", "starter")

    await db.execute(
        update(Organization)
        .where(Organization.id == org_id)
        .values(
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            subscription_tier=tier,
            subscription_status="active",
        )
    )
    await db.commit()


async def handle_subscription_updated(event_data: dict, db: AsyncSession) -> None:
    sub = event_data["object"]
    org_id = sub["metadata"].get("org_id")
    if not org_id:
        return

    status = sub["status"]           # active | past_due | canceled | trialing
    tier = sub["metadata"].get("tier", "starter")

    await db.execute(
        update(Organization)
        .where(Organization.id == org_id)
        .values(subscription_tier=tier, subscription_status=status)
    )
    await db.commit()


async def handle_subscription_deleted(event_data: dict, db: AsyncSession) -> None:
    sub = event_data["object"]
    org_id = sub["metadata"].get("org_id")
    if not org_id:
        return

    await db.execute(
        update(Organization)
        .where(Organization.id == org_id)
        .values(subscription_tier="free", subscription_status="canceled")
    )
    await db.commit()


async def handle_invoice_payment_failed(event_data: dict, db: AsyncSession) -> None:
    invoice = event_data["object"]
    sub_id = invoice.get("subscription")
    if not sub_id:
        return

    result = await db.execute(
        select(Organization).where(Organization.stripe_subscription_id == sub_id)
    )
    org = result.scalar_one_or_none()
    if org:
        await db.execute(
            update(Organization)
            .where(Organization.id == str(org.id))
            .values(subscription_status="past_due")
        )
        await db.commit()


# ──────────────────────────────────────────────
# Usage-based billing — certificate metering
# ──────────────────────────────────────────────

async def record_certificate_usage(org_id: str, db: AsyncSession, quantity: int = 1) -> None:
    """
    Report certificate usage to Stripe for metered billing.

    Called after every successful certificate generation.
    Only bills if org is on a paid subscription with overage pricing configured.
    """
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org or not org.stripe_subscription_id:
        return

    tier = getattr(org, "subscription_tier", "free") or "free"
    included = CERT_INCLUDED.get(tier, 0)
    if included == -1:
        return  # enterprise: unlimited, never bill overage

    # Increment usage counter on organization
    used = getattr(org, "certificates_used", 0) + quantity
    await db.execute(
        update(Organization)
        .where(Organization.id == org_id)
        .values(certificates_used=used)
    )
    await db.commit()

    # Only report to Stripe if overage price is configured
    if PRICE_CERT_OVERAGE == "price_cert_overage_placeholder":
        return

    # Find the subscription item with the metered price
    try:
        sub = stripe.Subscription.retrieve(org.stripe_subscription_id, expand=["items"])
        metered_item = next(
            (item for item in sub["items"]["data"] if item["price"]["id"] == PRICE_CERT_OVERAGE),
            None,
        )
        if metered_item:
            stripe.SubscriptionItem.create_usage_record(
                metered_item["id"],
                quantity=quantity,
                action="increment",
            )
    except stripe.StripeError:
        pass  # non-blocking — billing errors must never block cert delivery


async def get_certificate_usage(org_id: str, db: AsyncSession) -> dict:
    """Return current month certificate usage and limit for the org."""
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        return {"used": 0, "included": 0, "tier": "free"}

    tier = getattr(org, "subscription_tier", "free") or "free"
    included = CERT_INCLUDED.get(tier, 0)
    used = getattr(org, "certificates_used", 0)
    return {
        "used": used,
        "included": included,
        "overage": max(0, used - included) if included != -1 else 0,
        "tier": tier,
        "unlimited": included == -1,
    }


# ──────────────────────────────────────────────
# Query helpers
# ──────────────────────────────────────────────

async def get_subscription_info(org_id: str, db: AsyncSession) -> dict:
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        return {"tier": "free", "status": "none", "limits": TIER_LIMITS.get("starter", {})}

    tier = getattr(org, "subscription_tier", "free") or "free"
    status = getattr(org, "subscription_status", "none") or "none"
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["starter"])
    return {"tier": tier, "status": status, "limits": limits}

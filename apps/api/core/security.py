"""Security utilities: JWT verification, Clerk token validation."""
import hashlib
import hmac
from datetime import UTC, datetime

import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt

from core.config import get_settings

settings = get_settings()

CLERK_JWKS_URL = "https://api.clerk.com/v1/jwks"
_jwks_cache: dict | None = None


async def get_clerk_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            CLERK_JWKS_URL,
            headers={"Authorization": f"Bearer {settings.clerk_secret_key}"},
        )
        resp.raise_for_status()
        _jwks_cache = resp.json()
        return _jwks_cache


async def verify_clerk_token(token: str) -> dict:
    """Verify a Clerk session JWT and return the payload."""
    try:
        jwks = await get_clerk_jwks()
        # Extract kid from token header
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get("kid")
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: key not found",
            )
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        ) from exc


def verify_stripe_webhook(payload: bytes, sig_header: str) -> dict:
    """Verify Stripe webhook signature."""
    import stripe
    stripe.api_key = settings.stripe_secret_key
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
        return event
    except stripe.error.SignatureVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe signature",
        ) from exc

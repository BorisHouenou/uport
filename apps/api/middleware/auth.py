"""Clerk authentication middleware and dependency injection."""
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import verify_clerk_token

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Security(bearer_scheme)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Verify Clerk JWT and resolve the internal org UUID.

    Clerk puts its own org ID (e.g. org_xxx) in the JWT. All DB queries use
    the internal UUID from the organizations table, so we look it up here once
    and cache it on request.state to avoid repeated DB hits.
    """
    token = credentials.credentials
    payload = await verify_clerk_token(token)

    clerk_user_id = payload.get("sub")
    clerk_org_id = payload.get("org_id") or payload.get("o", {}).get("id")

    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Resolve Clerk org ID → internal org UUID
    internal_org_id: str | None = None
    if clerk_org_id:
        from models.organization import Organization
        result = await db.execute(
            select(Organization).where(Organization.clerk_org_id == clerk_org_id)
        )
        org = result.scalar_one_or_none()
        if org:
            internal_org_id = str(org.id)

    # Stamp on request.state for get_db() RLS context
    request.state.org_id = internal_org_id
    request.state.user_id = clerk_user_id

    return {
        "user_id": clerk_user_id,
        "org_id": internal_org_id,
        "clerk_org_id": clerk_org_id,
        "email": payload.get("email", ""),
        "role": payload.get("org_role", "member"),
    }


async def require_admin(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    if current_user.get("role") not in ("org:admin", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user


CurrentUser = Annotated[dict, Depends(get_current_user)]
AdminUser = Annotated[dict, Depends(require_admin)]

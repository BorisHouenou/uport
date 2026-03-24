"""Clerk authentication middleware and dependency injection."""
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.security import verify_clerk_token

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(bearer_scheme)],
) -> dict:
    """Extract and verify the current user from Clerk JWT."""
    token = credentials.credentials
    payload = await verify_clerk_token(token)
    user_id = payload.get("sub")
    org_id = payload.get("org_id") or payload.get("o", {}).get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return {
        "user_id": user_id,
        "org_id": org_id,
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

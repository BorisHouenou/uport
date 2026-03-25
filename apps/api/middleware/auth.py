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
    user = {
        "user_id": user_id,
        "org_id": org_id,
        "email": payload.get("email", ""),
        "role": payload.get("org_role", "member"),
    }

    # Stamp org_id on request.state so get_db() can set the RLS context variable
    try:
        from starlette.requests import Request as StarletteRequest
        import inspect
        frame = inspect.currentframe()
        # Walk up the call stack to find the Request object
        for fi in inspect.getouterframes(frame):
            local_vars = fi.frame.f_locals
            req = local_vars.get("request") or local_vars.get("req")
            if req is not None and hasattr(req, "state"):
                req.state.org_id = org_id
                req.state.user_id = user_id
                break
    except Exception:
        pass

    return user


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

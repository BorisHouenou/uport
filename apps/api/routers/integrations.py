"""Third-party integration endpoints (QuickBooks Online, etc.)."""
import secrets
from urllib.parse import urljoin

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.database import get_db
from middleware.auth import CurrentUser

router = APIRouter(prefix="/integrations", tags=["integrations"])
settings = get_settings()


# ─── QuickBooks Online ─────────────────────────────────────────────────────────

@router.get("/qbo/connect")
async def qbo_connect(
    request: Request,
    current_user: CurrentUser,
):
    """Return the QBO OAuth2 authorization URL."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages/integrations"))
    from quickbooks.oauth import get_auth_url

    state = f"{current_user['org_id']}:{secrets.token_urlsafe(16)}"
    redirect_uri = str(request.url_for("qbo_callback"))
    url = get_auth_url(redirect_uri=redirect_uri, state=state)
    return {"auth_url": url, "state": state}


@router.get("/qbo/callback", name="qbo_callback", include_in_schema=False)
async def qbo_callback(
    code: str = Query(...),
    state: str = Query(...),
    realmId: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle QBO OAuth2 callback and persist tokens."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages/integrations"))
    from quickbooks.oauth import exchange_code
    from services.integration_service import save_qbo_tokens

    # state = "{org_id}:{nonce}"
    org_id = state.split(":")[0]
    redirect_uri = f"{settings.api_base_url}/api/v1/integrations/qbo/callback"

    tokens = await exchange_code(code=code, redirect_uri=redirect_uri, realm_id=realmId)
    await save_qbo_tokens(db, org_id, tokens)

    # Redirect to frontend settings page
    return {"message": "QuickBooks connected", "realm_id": realmId}


@router.get("/qbo/status")
async def qbo_status(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return whether QBO is connected for the org."""
    from services.integration_service import get_qbo_connection
    conn = await get_qbo_connection(db, current_user["org_id"])
    return {"connected": conn is not None, "realm_id": conn.get("realm_id") if conn else None}


@router.post("/qbo/disconnect")
async def qbo_disconnect(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Revoke QBO tokens and remove connection."""
    from services.integration_service import remove_qbo_connection
    await remove_qbo_connection(db, current_user["org_id"])
    return {"disconnected": True}


@router.get("/qbo/items")
async def qbo_items(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Fetch Items from QBO and return as BOM-compatible rows."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages/integrations"))
    from quickbooks.client import QuickBooksClient, qbo_item_to_bom_row
    from services.integration_service import get_qbo_connection, maybe_refresh_qbo_token

    conn = await get_qbo_connection(db, current_user["org_id"])
    if not conn:
        raise HTTPException(status_code=400, detail="QuickBooks not connected")

    access_token = await maybe_refresh_qbo_token(db, current_user["org_id"], conn)
    sandbox = settings.environment != "production"
    client = QuickBooksClient(access_token, conn["realm_id"], sandbox=sandbox)

    items = await client.list_items()
    return {"items": [qbo_item_to_bom_row(i) for i in items], "count": len(items)}


class QBOImportRequest(BaseModel):
    product_id: str
    item_ids: list[str] | None = None  # None = import all


@router.post("/qbo/import-bom")
async def qbo_import_bom(
    body: QBOImportRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Import QBO items as BOM lines for a product, triggering AI HS classification."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages/integrations"))
    from quickbooks.client import QuickBooksClient, qbo_item_to_bom_row
    from services.integration_service import get_qbo_connection, maybe_refresh_qbo_token
    from services.tasks.bom_tasks import process_bom_from_rows

    conn = await get_qbo_connection(db, current_user["org_id"])
    if not conn:
        raise HTTPException(status_code=400, detail="QuickBooks not connected")

    access_token = await maybe_refresh_qbo_token(db, current_user["org_id"], conn)
    sandbox = settings.environment != "production"
    client = QuickBooksClient(access_token, conn["realm_id"], sandbox=sandbox)

    items = await client.list_items()
    if body.item_ids:
        items = [i for i in items if i.get("Id") in body.item_ids]

    rows = [qbo_item_to_bom_row(i) for i in items]

    # Dispatch Celery task — async HS classification + BOM save
    task = process_bom_from_rows.delay(
        product_id=body.product_id,
        rows=rows,
        org_id=current_user["org_id"],
    )
    return {"task_id": task.id, "items_queued": len(rows)}

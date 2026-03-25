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


_INTEGRATIONS_PATH = __import__("os").path.join(
    __import__("os").path.dirname(__file__), "../../../../packages/integrations"
)


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


# ─── NetSuite ──────────────────────────────────────────────────────────────────

class NetSuiteCredentials(BaseModel):
    account_id: str
    consumer_key: str
    consumer_secret: str
    token_id: str
    token_secret: str


class NetSuiteImportRequest(BaseModel):
    product_id: str
    assembly_item_id: str
    credentials: NetSuiteCredentials


@router.post("/netsuite/import-bom")
async def netsuite_import_bom(
    body: NetSuiteImportRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Import BOM from a NetSuite assembly item."""
    import sys
    sys.path.insert(0, _INTEGRATIONS_PATH)
    from netsuite.client import NetSuiteClient
    from services.tasks.bom_tasks import process_bom_from_rows

    creds = body.credentials
    client = NetSuiteClient(
        account_id=creds.account_id,
        consumer_key=creds.consumer_key,
        consumer_secret=creds.consumer_secret,
        token_id=creds.token_id,
        token_secret=creds.token_secret,
    )
    rows = client.get_bom(body.assembly_item_id)
    if not rows:
        raise HTTPException(status_code=404, detail="No BOM components found for this assembly item")

    task = process_bom_from_rows.delay(
        product_id=body.product_id,
        rows=rows,
        org_id=current_user["org_id"],
    )
    return {"task_id": task.id, "items_queued": len(rows)}


@router.get("/netsuite/items")
async def netsuite_items(
    account_id: str,
    consumer_key: str,
    consumer_secret: str,
    token_id: str,
    token_secret: str,
    current_user: CurrentUser,
):
    """List NetSuite inventory items (credential params passed as query for testing)."""
    import sys
    sys.path.insert(0, _INTEGRATIONS_PATH)
    from netsuite.client import NetSuiteClient

    client = NetSuiteClient(account_id, consumer_key, consumer_secret, token_id, token_secret)
    items = client.get_items(limit=50)
    return {"items": items, "count": len(items)}


# ─── Flexport ──────────────────────────────────────────────────────────────────

class FlexportSyncRequest(BaseModel):
    api_key: str
    page: int = 1
    limit: int = 50


@router.post("/flexport/sync-shipments")
async def flexport_sync_shipments(
    body: FlexportSyncRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Pull Flexport shipments and create Uportai shipment records."""
    import sys, uuid as _uuid
    sys.path.insert(0, _INTEGRATIONS_PATH)
    from flexport.client import FlexportClient
    from models import Shipment
    from sqlalchemy import select

    client = FlexportClient(body.api_key)
    shipments = client.get_shipments(per_page=body.limit, page=body.page)

    org_id = _uuid.UUID(current_user["org_id"])
    created = 0
    for s in shipments:
        if not s.get("origin_country") or not s.get("destination_country"):
            continue
        existing = (await db.execute(
            select(Shipment).where(Shipment.reference_number == s["reference_number"])
            .where(Shipment.org_id == org_id)
        )).scalar_one_or_none()
        if existing:
            continue
        db.add(Shipment(
            org_id=org_id,
            reference_number=s["reference_number"],
            origin_country=s["origin_country"],
            destination_country=s["destination_country"],
            incoterm=s.get("incoterm"),
            status=s.get("status", "pending"),
            shipment_value_usd=s.get("shipment_value_usd"),
        ))
        created += 1

    await db.commit()
    return {"synced": len(shipments), "created": created}


# ─── SAP B1 ───────────────────────────────────────────────────────────────────

class SAPB1ImportRequest(BaseModel):
    product_id: str
    item_code: str
    base_url: str
    company_db: str
    username: str
    password: str


@router.post("/sap-b1/import-bom")
async def sap_b1_import_bom(
    body: SAPB1ImportRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Import BOM from SAP Business One."""
    import sys
    sys.path.insert(0, _INTEGRATIONS_PATH)
    from sap_b1.client import SAPB1Client
    from services.tasks.bom_tasks import process_bom_from_rows

    client = SAPB1Client(body.base_url, body.company_db, body.username, body.password)
    client.login()
    try:
        rows = client.get_bom(body.item_code)
    finally:
        client.logout()

    if not rows:
        raise HTTPException(status_code=404, detail="No BOM found for this item code")

    task = process_bom_from_rows.delay(
        product_id=body.product_id,
        rows=rows,
        org_id=current_user["org_id"],
    )
    return {"task_id": task.id, "items_queued": len(rows)}


# ─── ShipBob ──────────────────────────────────────────────────────────────────

class ShipbobSyncRequest(BaseModel):
    personal_access_token: str
    page: int = 1
    limit: int = 50


@router.post("/shipbob/sync-shipments")
async def shipbob_sync_shipments(
    body: ShipbobSyncRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Pull ShipBob shipments and create Uportai shipment records."""
    import sys, uuid as _uuid
    sys.path.insert(0, _INTEGRATIONS_PATH)
    from shipbob.client import ShipbobClient
    from models import Shipment
    from sqlalchemy import select

    client = ShipbobClient(body.personal_access_token)
    shipments = client.get_shipments(page=body.page, limit=body.limit)

    org_id = _uuid.UUID(current_user["org_id"])
    created = 0
    for s in shipments:
        if not s.get("destination_country"):
            continue
        existing = (await db.execute(
            select(Shipment).where(Shipment.reference_number == s["reference_number"])
            .where(Shipment.org_id == org_id)
        )).scalar_one_or_none()
        if existing:
            continue
        db.add(Shipment(
            org_id=org_id,
            reference_number=s["reference_number"],
            origin_country=s.get("origin_country", "US"),
            destination_country=s["destination_country"],
            status=s.get("status", "pending"),
        ))
        created += 1

    await db.commit()
    return {"synced": len(shipments), "created": created}

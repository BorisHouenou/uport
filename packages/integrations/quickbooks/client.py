"""QuickBooks Online API client — Items and Accounts."""
from __future__ import annotations

from typing import Any

import httpx

QBO_API_BASE = "https://quickbooks.api.intuit.com/v3/company"
QBO_SANDBOX_BASE = "https://sandbox-quickbooks.api.intuit.com/v3/company"


class QuickBooksClient:
    """
    Thin async client for the QBO v3 API.

    Usage:
        client = QuickBooksClient(access_token, realm_id, sandbox=True)
        items = await client.list_items()
    """

    def __init__(self, access_token: str, realm_id: str, sandbox: bool = False):
        self._token = access_token
        self._realm = realm_id
        self._base = (QBO_SANDBOX_BASE if sandbox else QBO_API_BASE) + f"/{realm_id}"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def query(self, sql: str) -> dict[str, Any]:
        """Run a QBO SQL-like query (e.g. SELECT * FROM Item)."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self._base}/query",
                params={"query": sql, "minorversion": "65"},
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def list_items(self, max_results: int = 200) -> list[dict[str, Any]]:
        """Fetch all inventory/service items from QBO."""
        sql = f"SELECT * FROM Item WHERE Active = true MAXRESULTS {max_results}"
        data = await self.query(sql)
        return data.get("QueryResponse", {}).get("Item", [])

    async def get_item(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self._base}/item/{item_id}",
                params={"minorversion": "65"},
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json().get("Item", {})

    async def list_vendors(self, max_results: int = 200) -> list[dict[str, Any]]:
        sql = f"SELECT * FROM Vendor WHERE Active = true MAXRESULTS {max_results}"
        data = await self.query(sql)
        return data.get("QueryResponse", {}).get("Vendor", [])

    async def list_purchase_orders(self, max_results: int = 100) -> list[dict[str, Any]]:
        sql = f"SELECT * FROM PurchaseOrder MAXRESULTS {max_results}"
        data = await self.query(sql)
        return data.get("QueryResponse", {}).get("PurchaseOrder", [])


def qbo_item_to_bom_row(item: dict[str, Any]) -> dict[str, Any]:
    """
    Map a QBO Item object to an Uportai BOM row shape.

    Returns dict compatible with BOMRow (packages/ai-agents/bom_parser.py).
    """
    return {
        "description": item.get("Description") or item.get("Name", ""),
        "quantity": item.get("QtyOnHand") or 1.0,
        "unit_cost": (item.get("PurchaseCost") or item.get("UnitPrice") or 0.0),
        "currency": "USD",
        "origin_country": None,  # enriched later via supplier declarations
        "hs_code": None,         # classified by AI after import
        "is_originating": None,
        "source": f"quickbooks:item:{item.get('Id', '')}",
    }

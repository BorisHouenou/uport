"""
SAP Business One Service Layer client.

SAP B1 Service Layer uses cookie-based session auth (B1SESSION cookie).
Login returns a session cookie valid for 30 minutes (configurable).

Docs: https://help.sap.com/docs/SAP_BUSINESS_ONE/68a2e87fb29941b5bf959a184d9c6727/
"""
from typing import Any

import httpx


class SAPB1Client:
    def __init__(self, base_url: str, company_db: str, username: str, password: str):
        """
        base_url:   e.g. "https://sap-b1.yourcompany.com:50000/b1s/v1"
        company_db: SAP B1 company database name
        """
        self.base_url = base_url.rstrip("/")
        self.company_db = company_db
        self.username = username
        self.password = password
        self._session_cookie: str | None = None

    # ── Session ────────────────────────────────────────────────────────────────

    def login(self) -> None:
        """Authenticate and store the B1SESSION cookie."""
        with httpx.Client(verify=False, timeout=30) as client:  # noqa: S501 — SAP B1 uses self-signed certs
            resp = client.post(
                f"{self.base_url}/Login",
                json={
                    "CompanyDB": self.company_db,
                    "UserName": self.username,
                    "Password": self.password,
                },
            )
            resp.raise_for_status()
            self._session_cookie = resp.cookies.get("B1SESSION")
            if not self._session_cookie:
                raise RuntimeError("SAP B1 login did not return a B1SESSION cookie")

    def logout(self) -> None:
        if self._session_cookie:
            try:
                self._post("/Logout", {})
            except Exception:
                pass
            self._session_cookie = None

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_items(self, skip: int = 0, top: int = 100) -> list[dict]:
        """Fetch Items master data."""
        resp = self._get("/Items", params={"$skip": skip, "$top": top})
        return [_sap_item_to_bom_row(i) for i in resp.get("value", [])]

    def get_bom(self, item_code: str) -> list[dict]:
        """
        Fetch Bill of Materials for a finished good.
        SAP B1 stores BOMs under ProductionOrders or the SpecialPrices entity.
        """
        resp = self._get(
            "/ProductionOrders",
            params={
                "$filter": f"ItemNo eq '{item_code}' and ProductionOrderType eq 'boStandard'",
                "$top": 1,
            },
        )
        orders = resp.get("value", [])
        if not orders:
            return []
        lines = orders[0].get("ProductionOrderLines", [])
        return [_sap_bom_line_to_row(line) for line in lines]

    # ── HTTP ───────────────────────────────────────────────────────────────────

    def _get(self, path: str, params: dict | None = None) -> dict:
        if not self._session_cookie:
            self.login()
        with httpx.Client(verify=False, timeout=30) as client:  # noqa: S501
            resp = client.get(
                self.base_url + path,
                params=params,
                cookies={"B1SESSION": self._session_cookie},
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return resp.json()

    def _post(self, path: str, body: dict) -> dict:
        if not self._session_cookie:
            self.login()
        with httpx.Client(verify=False, timeout=30) as client:  # noqa: S501
            resp = client.post(
                self.base_url + path,
                json=body,
                cookies={"B1SESSION": self._session_cookie},
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return resp.json() if resp.content else {}


def _sap_item_to_bom_row(item: dict) -> dict:
    return {
        "component_id":  item.get("ItemCode", ""),
        "description":   item.get("ItemName", ""),
        "quantity":      1.0,
        "unit":          item.get("SalesUnitOfMeasure") or item.get("InventoryUOM", "each"),
        "hs_code":       item.get("NCMCode") or item.get("CustomsCode"),
        "origin_country": item.get("CountryOfOrigin"),
    }


def _sap_bom_line_to_row(line: dict) -> dict:
    return {
        "component_id":  line.get("ItemNo", ""),
        "description":   line.get("ProductionOrderLineItemDescription", ""),
        "quantity":      float(line.get("PlannedQuantity", 1)),
        "unit":          line.get("UnitOfMeasure", "each"),
        "hs_code":       None,
        "origin_country": None,
    }

"""
NetSuite REST API client — Token-Based Authentication (TBA / OAuth 1.0a).

NetSuite uses OAuth 1.0a (not 2.0) with four credentials:
  - Account ID
  - Consumer Key + Consumer Secret  (from Integration record)
  - Token ID + Token Secret          (from Access Token record)

Docs: https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/chapter_4407773929.html
"""
import hashlib
import hmac
import random
import string
import time
import urllib.parse
from typing import Any

import httpx


class NetSuiteClient:
    def __init__(
        self,
        account_id: str,
        consumer_key: str,
        consumer_secret: str,
        token_id: str,
        token_secret: str,
    ):
        self.account_id = account_id.lower().replace("_", "-")
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token_id = token_id
        self.token_secret = token_secret
        self.base_url = f"https://{self.account_id}.suitetalk.api.netsuite.com/services/rest/record/v1"

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_items(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Fetch inventory items from NetSuite."""
        resp = self._get("/inventoryItem", params={"limit": limit, "offset": offset})
        return resp.get("items", [])

    def get_bom(self, assembly_item_id: str) -> list[dict]:
        """
        Fetch Bill of Materials components for an assembly item.
        Returns list of {component_id, description, quantity, unit} rows.
        """
        resp = self._get(f"/assemblyItem/{assembly_item_id}/billOfMaterials")
        components = resp.get("components", {}).get("items", [])
        return [_netsuite_component_to_bom_row(c) for c in components]

    def search_items(self, query: str) -> list[dict]:
        """Full-text search for items by name/description."""
        resp = self._get("/inventoryItem", params={"q": query})
        return resp.get("items", [])

    # ── HTTP ───────────────────────────────────────────────────────────────────

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = self.base_url + path
        headers = self._auth_header("GET", url, params or {})
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()

    # ── OAuth 1.0a signing ─────────────────────────────────────────────────────

    def _auth_header(self, method: str, url: str, params: dict) -> dict:
        nonce = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        timestamp = str(int(time.time()))

        oauth_params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": nonce,
            "oauth_signature_method": "HMAC-SHA256",
            "oauth_timestamp": timestamp,
            "oauth_token": self.token_id,
            "oauth_version": "1.0",
        }

        # Build signature base string
        all_params = {**params, **oauth_params}
        sorted_params = "&".join(
            f"{urllib.parse.quote(str(k), safe='')}={urllib.parse.quote(str(v), safe='')}"
            for k, v in sorted(all_params.items())
        )
        base = "&".join([
            method.upper(),
            urllib.parse.quote(url, safe=""),
            urllib.parse.quote(sorted_params, safe=""),
        ])

        signing_key = f"{urllib.parse.quote(self.consumer_secret, safe='')}&{urllib.parse.quote(self.token_secret, safe='')}"
        signature = hmac.new(signing_key.encode(), base.encode(), hashlib.sha256)
        import base64
        oauth_params["oauth_signature"] = base64.b64encode(signature.digest()).decode()
        oauth_params["oauth_realm"] = self.account_id.upper().replace("-", "_")

        auth_value = "OAuth " + ", ".join(
            f'{k}="{urllib.parse.quote(str(v), safe="")}"'
            for k, v in oauth_params.items()
        )
        return {
            "Authorization": auth_value,
            "Content-Type": "application/json",
            "Prefer": "transient",
        }


def _netsuite_component_to_bom_row(component: dict) -> dict:
    return {
        "component_id": str(component.get("item", {}).get("id", "")),
        "description": component.get("item", {}).get("refName", ""),
        "quantity": float(component.get("quantity", 1)),
        "unit": component.get("units", {}).get("refName", "each"),
        "hs_code": None,
        "origin_country": None,
    }

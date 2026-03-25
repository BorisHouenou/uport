"""
Flexport API v2 client — API key authentication.

Fetches shipments and converts them to Uportai shipment records.
Docs: https://developers.flexport.com/
"""
from typing import Any

import httpx


BASE_URL = "https://api.flexport.com"


class FlexportClient:
    def __init__(self, api_key: str):
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Flexport-Version": "2",
        }

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_shipments(self, per_page: int = 50, page: int = 1) -> list[dict]:
        """Fetch ocean/air shipments from Flexport."""
        resp = self._get("/shipments", params={"per_page": per_page, "page": page})
        return [_flexport_shipment_to_uportai(s) for s in resp.get("data", [])]

    def get_shipment(self, shipment_id: str) -> dict:
        """Fetch a single shipment by Flexport ID."""
        resp = self._get(f"/shipments/{shipment_id}")
        return _flexport_shipment_to_uportai(resp.get("data", {}))

    def get_commercial_invoices(self, shipment_id: str) -> list[dict]:
        """Fetch commercial invoices (contains HS codes + line items)."""
        resp = self._get(f"/shipments/{shipment_id}/documents", params={"type": "commercial_invoice"})
        return resp.get("data", [])

    # ── HTTP ───────────────────────────────────────────────────────────────────

    def _get(self, path: str, params: dict | None = None) -> dict:
        with httpx.Client(timeout=30, base_url=BASE_URL) as client:
            resp = client.get(path, params=params, headers=self._headers)
            resp.raise_for_status()
            return resp.json()


def _flexport_shipment_to_uportai(s: dict) -> dict:
    """Map a Flexport shipment object to Uportai shipment fields."""
    origin = s.get("origin", {})
    dest   = s.get("destination", {})
    return {
        "flexport_id":           s.get("id"),
        "reference_number":      s.get("name") or s.get("id"),
        "origin_country":        (origin.get("address") or {}).get("country_code", ""),
        "destination_country":   (dest.get("address") or {}).get("country_code", ""),
        "incoterm":              s.get("incoterms"),
        "status":                _map_status(s.get("phase")),
        "shipment_value_usd":    _extract_value(s),
    }


def _map_status(phase: str | None) -> str:
    mapping = {
        "booking_initiated": "pending",
        "booking_confirmed": "pending",
        "in_transit":        "in_transit",
        "arrived":           "arrived",
        "delivered":         "completed",
    }
    return mapping.get(phase or "", "pending")


def _extract_value(s: dict) -> float | None:
    try:
        return float(s["cargo"]["total_value"]["amount"])
    except (KeyError, TypeError, ValueError):
        return None

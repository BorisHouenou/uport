"""
ShipBob API client — Personal Access Token (PAT) authentication.

ShipBob is a 3PL / fulfillment platform. We pull orders and shipments
to create Uportai shipment records with origin/destination data.

Docs: https://developer.shipbob.com/
"""
from typing import Any

import httpx

BASE_URL = "https://api.shipbob.com/1.0"


class ShipbobClient:
    def __init__(self, personal_access_token: str):
        self._headers = {
            "Authorization": f"Bearer {personal_access_token}",
            "Content-Type": "application/json",
        }

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_orders(self, page: int = 1, limit: int = 50) -> list[dict]:
        """Fetch orders from ShipBob."""
        resp = self._get("/order", params={"Page": page, "Limit": limit})
        return [_shipbob_order_to_uportai(o) for o in (resp if isinstance(resp, list) else [])]

    def get_shipments(self, page: int = 1, limit: int = 50) -> list[dict]:
        """Fetch shipments (fulfillments) from ShipBob."""
        resp = self._get("/shipment", params={"Page": page, "Limit": limit})
        return [_shipbob_shipment_to_uportai(s) for s in (resp if isinstance(resp, list) else [])]

    def get_products(self, page: int = 1, limit: int = 100) -> list[dict]:
        """Fetch product inventory from ShipBob."""
        resp = self._get("/product", params={"Page": page, "Limit": limit})
        return resp if isinstance(resp, list) else []

    # ── HTTP ───────────────────────────────────────────────────────────────────

    def _get(self, path: str, params: dict | None = None) -> Any:
        with httpx.Client(timeout=30, base_url=BASE_URL) as client:
            resp = client.get(path, params=params, headers=self._headers)
            resp.raise_for_status()
            return resp.json()


def _shipbob_order_to_uportai(order: dict) -> dict:
    recipient = order.get("recipient", {})
    address = recipient.get("address", {})
    return {
        "shipbob_order_id":    str(order.get("id", "")),
        "reference_number":    order.get("reference_id") or str(order.get("id", "")),
        "origin_country":      "US",  # ShipBob warehouses are US-based by default
        "destination_country": address.get("country", ""),
        "status":              _map_order_status(order.get("status")),
        "shipment_value_usd":  None,
    }


def _shipbob_shipment_to_uportai(shipment: dict) -> dict:
    return {
        "shipbob_shipment_id": str(shipment.get("id", "")),
        "reference_number":    str(shipment.get("id", "")),
        "origin_country":      "US",
        "destination_country": (shipment.get("recipient", {}).get("address") or {}).get("country", ""),
        "status":              _map_shipment_status(shipment.get("status")),
        "tracking_number":     shipment.get("tracking_number"),
        "carrier":             shipment.get("shipping_method"),
        "shipment_value_usd":  None,
    }


def _map_order_status(status: str | None) -> str:
    mapping = {
        "Processing": "pending",
        "Fulfilled":  "completed",
        "Cancelled":  "cancelled",
        "Exception":  "error",
    }
    return mapping.get(status or "", "pending")


def _map_shipment_status(status: str | None) -> str:
    mapping = {
        "LabelCreated":       "pending",
        "LabeledCreated":     "pending",
        "AttemptedDelivery":  "in_transit",
        "Delivered":          "completed",
        "Exception":          "error",
    }
    return mapping.get(status or "", "pending")

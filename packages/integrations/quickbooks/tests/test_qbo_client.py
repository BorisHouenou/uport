"""Unit tests for QuickBooks client helpers (no network calls)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from quickbooks.client import qbo_item_to_bom_row
from quickbooks.oauth import get_auth_url


# ─── qbo_item_to_bom_row ──────────────────────────────────────────────────────

class TestQBOItemToBOMRow:
    def _item(self, **overrides):
        base = {
            "Id": "42",
            "Name": "Steel Sheet 4x8",
            "Description": "Cold rolled steel sheet, 4x8 ft",
            "QtyOnHand": 150.0,
            "PurchaseCost": 12.50,
            "UnitPrice": 18.00,
            "Type": "Inventory",
        }
        return {**base, **overrides}

    def test_description_uses_description_field(self):
        row = qbo_item_to_bom_row(self._item())
        assert row["description"] == "Cold rolled steel sheet, 4x8 ft"

    def test_description_falls_back_to_name(self):
        item = self._item()
        del item["Description"]
        row = qbo_item_to_bom_row(item)
        assert row["description"] == "Steel Sheet 4x8"

    def test_quantity_from_qty_on_hand(self):
        row = qbo_item_to_bom_row(self._item())
        assert row["quantity"] == 150.0

    def test_quantity_defaults_to_1_when_missing(self):
        item = self._item()
        del item["QtyOnHand"]
        row = qbo_item_to_bom_row(item)
        assert row["quantity"] == 1.0

    def test_unit_cost_uses_purchase_cost(self):
        row = qbo_item_to_bom_row(self._item())
        assert row["unit_cost"] == 12.50

    def test_unit_cost_falls_back_to_unit_price(self):
        item = self._item()
        del item["PurchaseCost"]
        row = qbo_item_to_bom_row(item)
        assert row["unit_cost"] == 18.00

    def test_unit_cost_zero_when_both_missing(self):
        item = self._item()
        del item["PurchaseCost"]
        del item["UnitPrice"]
        row = qbo_item_to_bom_row(item)
        assert row["unit_cost"] == 0.0

    def test_currency_is_usd(self):
        row = qbo_item_to_bom_row(self._item())
        assert row["currency"] == "USD"

    def test_origin_country_is_none(self):
        row = qbo_item_to_bom_row(self._item())
        assert row["origin_country"] is None

    def test_hs_code_is_none(self):
        row = qbo_item_to_bom_row(self._item())
        assert row["hs_code"] is None

    def test_is_originating_is_none(self):
        row = qbo_item_to_bom_row(self._item())
        assert row["is_originating"] is None

    def test_source_contains_quickbooks_and_id(self):
        row = qbo_item_to_bom_row(self._item())
        assert row["source"] == "quickbooks:item:42"

    def test_source_with_empty_id(self):
        item = self._item()
        del item["Id"]
        row = qbo_item_to_bom_row(item)
        assert "quickbooks:item:" in row["source"]

    def test_empty_item_does_not_raise(self):
        row = qbo_item_to_bom_row({})
        assert row["description"] == ""
        assert row["quantity"] == 1.0
        assert row["unit_cost"] == 0.0


# ─── get_auth_url ─────────────────────────────────────────────────────────────

class TestGetAuthUrl:
    def test_contains_client_id_param(self):
        url = get_auth_url("https://app.example.com/callback", "state123")
        assert "client_id=" in url

    def test_contains_redirect_uri(self):
        url = get_auth_url("https://app.example.com/callback", "state123")
        assert "redirect_uri=" in url

    def test_contains_state(self):
        url = get_auth_url("https://app.example.com/callback", "mystate")
        assert "mystate" in url

    def test_contains_scope(self):
        url = get_auth_url("https://app.example.com/callback", "state123")
        assert "scope=" in url
        assert "quickbooks" in url

    def test_is_https(self):
        url = get_auth_url("https://app.example.com/callback", "state123")
        assert url.startswith("https://")

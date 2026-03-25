"""Unit tests for billing_service tier logic.

Uses AST parsing to extract TIER_LIMITS / PRICE_IDS without importing the
module (which has heavy SQLAlchemy + Stripe deps that aren't installed here).
"""
import ast
import os
import pytest

_SRC = os.path.join(os.path.dirname(__file__), "..", "services", "billing_service.py")

# ── Extract TIER_LIMITS and PRICE_IDS via static AST parse ────────────────────
TIER_LIMITS: dict = {}
PRICE_IDS: dict = {}

tree = ast.parse(open(_SRC).read())

def _extract_name_and_value(node):
    """Return (name, value_node) for both Assign and AnnAssign nodes."""
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                return target.id, node.value
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id, node.value
    return None, None

for node in ast.walk(tree):
    name, value = _extract_name_and_value(node)
    if name is None or value is None:
        continue
    if name == "TIER_LIMITS" and isinstance(value, ast.Dict):
        for k, v in zip(value.keys, value.values):
            TIER_LIMITS[ast.literal_eval(k)] = ast.literal_eval(v)
    elif name == "PRICE_IDS" and isinstance(value, ast.Dict):
        for k, v in zip(value.keys, value.values):
            key = ast.literal_eval(k)
            # os.getenv("ENV_VAR", "default") — grab the default (2nd arg)
            if isinstance(v, ast.Call) and len(v.args) >= 2:
                PRICE_IDS[key] = ast.literal_eval(v.args[1])


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestTierLimits:
    def test_all_tiers_defined(self):
        for tier in ("starter", "growth", "enterprise"):
            assert tier in TIER_LIMITS

    def test_starter_limits(self):
        s = TIER_LIMITS["starter"]
        assert s["shipments_per_month"] == 25
        assert s["users"] == 3
        assert s["api_access"] is False

    def test_growth_limits(self):
        g = TIER_LIMITS["growth"]
        assert g["shipments_per_month"] == 100
        assert g["users"] == 10
        assert g["api_access"] is True

    def test_enterprise_unlimited(self):
        e = TIER_LIMITS["enterprise"]
        assert e["shipments_per_month"] == -1
        assert e["users"] == -1
        assert e["api_access"] is True

    def test_growth_shipments_exceed_starter(self):
        assert TIER_LIMITS["growth"]["shipments_per_month"] > TIER_LIMITS["starter"]["shipments_per_month"]

    def test_enterprise_users_unlimited(self):
        assert TIER_LIMITS["enterprise"]["users"] == -1

    def test_all_tiers_have_required_keys(self):
        required = {"shipments_per_month", "users", "api_access"}
        for tier, limits in TIER_LIMITS.items():
            assert required <= limits.keys(), f"Tier '{tier}' missing keys: {required - limits.keys()}"

    def test_starter_no_api_access(self):
        assert TIER_LIMITS["starter"]["api_access"] is False

    def test_growth_and_enterprise_have_api_access(self):
        assert TIER_LIMITS["growth"]["api_access"] is True
        assert TIER_LIMITS["enterprise"]["api_access"] is True


class TestPriceIds:
    def test_all_tiers_have_price_id(self):
        for tier in ("starter", "growth", "enterprise"):
            assert tier in PRICE_IDS, f"Missing price ID for tier '{tier}'"
            assert PRICE_IDS[tier], f"Empty price ID for tier '{tier}'"

    def test_price_ids_are_strings(self):
        for tier, price_id in PRICE_IDS.items():
            assert isinstance(price_id, str), f"Price ID for '{tier}' is not a string"

    def test_price_ids_are_unique(self):
        ids = list(PRICE_IDS.values())
        assert len(ids) == len(set(ids)), f"Duplicate price IDs found: {ids}"

    def test_three_price_ids_total(self):
        assert len(PRICE_IDS) == 3

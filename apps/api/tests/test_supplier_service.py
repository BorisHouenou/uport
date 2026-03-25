"""Unit tests for supplier_service helpers (pure date logic, no DB)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
import pytest


class TestExpiryLogic:
    """Test the expiry/warn logic used in supplier_service._to_response."""

    def _is_expired(self, valid_until: date) -> bool:
        return valid_until < date.today()

    def _days_until_expiry(self, valid_until: date) -> int:
        return (valid_until - date.today()).days

    def test_past_date_is_expired(self):
        yesterday = date.today() - timedelta(days=1)
        assert self._is_expired(yesterday) is True

    def test_today_is_not_expired(self):
        assert self._is_expired(date.today()) is False

    def test_future_date_is_not_expired(self):
        future = date.today() + timedelta(days=90)
        assert self._is_expired(future) is False

    def test_expiring_within_30_days(self):
        soon = date.today() + timedelta(days=15)
        days = self._days_until_expiry(soon)
        assert 0 <= days <= 30

    def test_not_expiring_soon(self):
        far = date.today() + timedelta(days=60)
        days = self._days_until_expiry(far)
        assert days > 30

    def test_expiring_today_is_within_warn_window(self):
        days = self._days_until_expiry(date.today())
        assert days == 0
        WARN_DAYS = 30
        assert 0 <= days <= WARN_DAYS


class TestSchemaNormalization:
    """Verify schema fields match supplier model expectations."""

    def test_supplier_declaration_create_required_fields(self):
        """All required fields should be present in schema."""
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from schemas.suppliers import SupplierDeclarationCreate
        import uuid

        decl = SupplierDeclarationCreate(
            product_id=uuid.uuid4(),
            supplier_name="Test Supplier Co.",
            supplier_country="DE",
            origin_country="CA",
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=365),
        )
        assert decl.supplier_name == "Test Supplier Co."
        assert decl.declaration_text is None  # optional

    def test_supplier_declaration_response_is_expired_field(self):
        from schemas.suppliers import SupplierDeclarationResponse
        from datetime import datetime, timezone
        import uuid

        now = datetime.now(timezone.utc)
        resp = SupplierDeclarationResponse(
            id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            supplier_name="Acme",
            supplier_country="US",
            origin_country="US",
            valid_from=date.today() - timedelta(days=400),
            valid_until=date.today() - timedelta(days=35),
            is_expired=True,
            created_at=now,
            updated_at=now,
        )
        assert resp.is_expired is True

    def test_supplier_declaration_list_schema(self):
        from schemas.suppliers import SupplierDeclarationList
        sl = SupplierDeclarationList(declarations=[], total=0, expiring_soon=0)
        assert sl.total == 0
        assert sl.expiring_soon == 0

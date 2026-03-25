"""Unit tests for RVC calculations."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from models import BOMLine
from rvc import calculate_build_down, calculate_build_up, calculate_net_cost, best_rvc_method


def make_bom(orig_usd: float, non_orig_usd: float) -> list[BOMLine]:
    lines = []
    if orig_usd > 0:
        lines.append(BOMLine(description="Originating component", hs_code="7326.90", origin_country="CA", unit_cost=orig_usd, is_originating=True))
    if non_orig_usd > 0:
        lines.append(BOMLine(description="Non-originating component", hs_code="8544.42", origin_country="CN", unit_cost=non_orig_usd, is_originating=False))
    return lines


class TestBuildDown:
    def test_passes_40pct_threshold(self):
        bom = make_bom(orig_usd=70, non_orig_usd=30)
        result = calculate_build_down(bom, transaction_value_usd=100, threshold_pct=40)
        assert result.passes is True
        assert result.rvc_pct == 70.0
        assert result.method == "build_down"

    def test_fails_below_threshold(self):
        bom = make_bom(orig_usd=30, non_orig_usd=70)
        result = calculate_build_down(bom, transaction_value_usd=100, threshold_pct=40)
        assert result.passes is False
        assert result.rvc_pct == 30.0

    def test_exactly_at_threshold_passes(self):
        bom = make_bom(orig_usd=60, non_orig_usd=40)
        result = calculate_build_down(bom, transaction_value_usd=100, threshold_pct=40)
        assert result.passes is True
        assert result.rvc_pct == 60.0

    def test_zero_transaction_value_fails(self):
        bom = make_bom(orig_usd=50, non_orig_usd=50)
        result = calculate_build_down(bom, transaction_value_usd=0)
        assert result.passes is False

    def test_45pct_ceta_threshold(self):
        bom = make_bom(orig_usd=60, non_orig_usd=40)
        result = calculate_build_down(bom, transaction_value_usd=100, threshold_pct=45)
        assert result.passes is True  # 60% > 45%

    def test_unknown_origin_treated_as_non_originating(self):
        bom = [BOMLine(description="Unknown part", hs_code="7326.90", origin_country="CN", unit_cost=50, is_originating=None)]
        result = calculate_build_down(bom, transaction_value_usd=100, threshold_pct=40)
        assert result.rvc_pct == 50.0  # (100-50)/100


class TestBuildUp:
    def test_passes(self):
        bom = make_bom(orig_usd=50, non_orig_usd=50)
        result = calculate_build_up(bom, transaction_value_usd=100, threshold_pct=40)
        assert result.passes is True
        assert result.rvc_pct == 50.0

    def test_fails(self):
        bom = make_bom(orig_usd=20, non_orig_usd=80)
        result = calculate_build_up(bom, transaction_value_usd=100, threshold_pct=40)
        assert result.passes is False
        assert result.rvc_pct == 20.0


class TestNetCost:
    def test_passes(self):
        bom = make_bom(orig_usd=60, non_orig_usd=30)
        result = calculate_net_cost(bom, transaction_value_usd=100, net_cost_usd=90, threshold_pct=35)
        # RVC = (90-30)/90 = 66.7%
        assert result.passes is True
        assert abs(result.rvc_pct - 66.67) < 0.1

    def test_zero_net_cost_fails(self):
        bom = make_bom(orig_usd=60, non_orig_usd=30)
        result = calculate_net_cost(bom, transaction_value_usd=100, net_cost_usd=0, threshold_pct=35)
        assert result.passes is False


class TestBestMethod:
    def test_selects_highest_passing_rvc(self):
        bom = make_bom(orig_usd=55, non_orig_usd=45)
        result = best_rvc_method(bom, transaction_value_usd=100, threshold_pct=40)
        assert result.passes is True
        # Build-down = 55%, Build-up = 55% (same here since VOM=TV-VNM)

    def test_selects_best_when_all_fail(self):
        bom = make_bom(orig_usd=20, non_orig_usd=80)
        result = best_rvc_method(bom, transaction_value_usd=100, threshold_pct=40)
        assert result.passes is False
        assert result.rvc_pct == 20.0  # best among failing

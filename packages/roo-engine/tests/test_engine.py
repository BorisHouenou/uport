"""Integration tests for the full RoO engine."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import BOMLine, ProductInfo, RooRule, RuleType
from engine import RooEngine


def make_product(bom_lines, tv=100.0) -> ProductInfo:
    return ProductInfo(
        hs_code="8703.22",
        description="Passenger motor vehicle",
        transaction_value_usd=tv,
        bom=bom_lines,
        production_country="CA",
    )


def make_rvc_rule(agreement="cusma", threshold=40.0, method="build_down") -> RooRule:
    return RooRule(
        agreement_code=agreement,
        hs_heading="8703",
        rule_type=RuleType.RVC_BUILD_DOWN if method == "build_down" else RuleType.RVC_BUILD_UP,
        rule_text=f"RVC not less than {threshold}% (Build-Down method)",
        value_threshold=threshold,
        rvc_method=method,
    )


def make_ts_rule(agreement="cusma", level="heading") -> RooRule:
    return RooRule(
        agreement_code=agreement,
        hs_heading="8703",
        rule_type=RuleType.TARIFF_SHIFT,
        rule_text="CTH — Change in Tariff Heading",
        ts_heading_level=level,
    )


def make_bom(orig: float, non_orig: float) -> list[BOMLine]:
    lines = []
    if orig > 0:
        lines.append(BOMLine(description="Originating part", hs_code="7326.90", origin_country="CA", unit_cost=orig, is_originating=True))
    if non_orig > 0:
        lines.append(BOMLine(description="Non-originating part", hs_code="8544.42", origin_country="CN", unit_cost=non_orig, is_originating=False))
    return lines


class TestRooEngine:
    def setup_method(self):
        self.engine = RooEngine()

    def test_rvc_pass(self):
        product = make_product(make_bom(70, 30), tv=100)
        rules = {"cusma": [make_rvc_rule("cusma", 40)]}
        output = self.engine.evaluate(product, rules)
        assert output.best_agreement == "cusma"
        assert any(d.result.value == "pass" for d in output.determinations)

    def test_rvc_fail(self):
        product = make_product(make_bom(20, 80), tv=100)
        rules = {"cusma": [make_rvc_rule("cusma", 40)]}
        output = self.engine.evaluate(product, rules)
        assert output.best_agreement is None
        assert all(d.result.value == "fail" for d in output.determinations)

    def test_tariff_shift_pass(self):
        bom = [BOMLine(description="Part", hs_code="7326.90", origin_country="CN", unit_cost=50, is_originating=False)]
        product = make_product(bom)
        rules = {"cusma": [make_ts_rule("cusma", "heading")]}
        output = self.engine.evaluate(product, rules)
        # HS 7326 heading != 8703 → should pass
        assert output.best_agreement == "cusma"

    def test_tariff_shift_fail(self):
        bom = [BOMLine(description="Same heading part", hs_code="8703.10", origin_country="CN", unit_cost=50, is_originating=False)]
        product = make_product(bom)
        rules = {"cusma": [make_ts_rule("cusma", "heading")]}
        output = self.engine.evaluate(product, rules)
        assert output.best_agreement is None

    def test_multi_agreement_best_pick(self):
        product = make_product(make_bom(70, 30), tv=100)
        rules = {
            "cusma": [make_rvc_rule("cusma", 40)],
            "ceta": [make_rvc_rule("ceta", 45)],
        }
        output = self.engine.evaluate(product, rules)
        assert output.best_agreement in ("cusma", "ceta")
        assert len(output.determinations) == 2

    def test_no_bom_returns_insufficient(self):
        product = make_product([], tv=100)
        rules = {"cusma": [make_rvc_rule()]}
        output = self.engine.evaluate(product, rules)
        assert output.determinations[0].result.value == "insufficient_data"

    def test_wholly_obtained_pass(self):
        product = ProductInfo(
            hs_code="0101.21",
            description="Live thoroughbred horse",
            transaction_value_usd=5000,
            bom=[],
            production_country="CA",
            wholly_obtained_category="animal_born",
        )
        rule = RooRule(
            agreement_code="cusma",
            hs_chapter="01",
            rule_type=RuleType.WHOLLY_OBTAINED,
            rule_text="Wholly obtained in the territory of a Party",
        )
        output = self.engine.evaluate(product, {"cusma": [rule]})
        assert output.best_agreement == "cusma"
        assert output.determinations[0].result.value == "pass"

"""
RoO Compliance Engine — main orchestrator.

Usage:
    from engine import RooEngine
    from models import ProductInfo, RooRule, RuleType

    engine = RooEngine()
    output = engine.evaluate(product, rules_by_agreement)
"""
from __future__ import annotations

import structlog

from models import (
    AgreementDetermination,
    BOMLine,
    DeterminationResult,
    EngineOutput,
    ProductInfo,
    RooRule,
    RuleType,
    RVCResult,
    TariffShiftResult,
    WhollyObtainedResult,
)
from rvc import best_rvc_method, calculate_build_down, calculate_build_up, calculate_net_cost
from tariff_shift import evaluate_tariff_shift
from wholly_obtained import check_wholly_obtained

logger = structlog.get_logger()

# Below this confidence we flag for human review
HUMAN_REVIEW_THRESHOLD = 0.75


class RooEngine:
    """
    Evaluates Rules of Origin for a product against one or more trade agreements.
    Deterministic, testable, no AI dependencies.
    """

    def evaluate(
        self,
        product: ProductInfo,
        rules: dict[str, list[RooRule]],  # agreement_code → rules
    ) -> EngineOutput:
        """
        Evaluate a product against all provided agreement rules.

        Args:
            product: the finished good with BOM, transaction value, etc.
            rules: dict mapping agreement code to list of applicable RooRules

        Returns:
            EngineOutput with determinations per agreement and best pick.
        """
        determinations: list[AgreementDetermination] = []
        review_reasons: list[str] = []

        for agreement_code, agreement_rules in rules.items():
            for rule in agreement_rules:
                det = self._apply_rule(product, rule, agreement_code)
                determinations.append(det)
                if det.confidence < HUMAN_REVIEW_THRESHOLD:
                    review_reasons.append(
                        f"{agreement_code}: confidence {det.confidence:.0%} — {rule.rule_type}"
                    )

        # Pick best passing agreement (highest savings, or first pass)
        passing = [d for d in determinations if d.result == DeterminationResult.PASS]
        best: AgreementDetermination | None = None
        if passing:
            best = max(
                passing,
                key=lambda d: d.savings_per_unit or 0.0,
            )

        return EngineOutput(
            product_hs=product.hs_code,
            production_country=product.production_country,
            agreements_evaluated=list(rules.keys()),
            determinations=determinations,
            best_agreement=best.agreement_code if best else None,
            best_saving_usd=best.savings_per_unit if best else None,
            needs_human_review=len(review_reasons) > 0,
            review_reasons=review_reasons,
        )

    # ─── Rule dispatchers ─────────────────────────────────────────────────────

    def _apply_rule(
        self,
        product: ProductInfo,
        rule: RooRule,
        agreement_code: str,
    ) -> AgreementDetermination:
        """Dispatch to the appropriate rule evaluation method."""
        try:
            if rule.rule_type == RuleType.WHOLLY_OBTAINED:
                return self._eval_wholly_obtained(product, rule, agreement_code)
            elif rule.rule_type == RuleType.TARIFF_SHIFT:
                return self._eval_tariff_shift(product, rule, agreement_code)
            elif rule.rule_type in (RuleType.RVC_BUILD_DOWN, RuleType.RVC_BUILD_UP, RuleType.RVC_NET_COST):
                return self._eval_rvc(product, rule, agreement_code)
            elif rule.rule_type == RuleType.COMBINED:
                return self._eval_combined(product, rule, agreement_code)
            else:
                return self._insufficient(product, rule, agreement_code, "Unknown rule type")
        except Exception as exc:
            logger.warning("rule_evaluation_error", agreement=agreement_code, rule_type=rule.rule_type, error=str(exc))
            return self._insufficient(product, rule, agreement_code, str(exc))

    def _eval_wholly_obtained(self, product: ProductInfo, rule: RooRule, agreement_code: str) -> AgreementDetermination:
        wo = check_wholly_obtained(
            production_country=product.production_country,
            category=product.wholly_obtained_category,
            agreement_code=agreement_code,
        )
        result = DeterminationResult.PASS if wo.passes else DeterminationResult.FAIL
        confidence = 0.95 if wo.passes else (0.5 if product.wholly_obtained_category is None else 0.9)
        return AgreementDetermination(
            agreement_code=agreement_code,
            rule_applied=RuleType.WHOLLY_OBTAINED,
            rule_text=rule.rule_text,
            result=result,
            confidence=confidence,
            reasoning=wo.detail,
            wo_result=wo,
        )

    def _eval_tariff_shift(self, product: ProductInfo, rule: RooRule, agreement_code: str) -> AgreementDetermination:
        if not product.bom:
            return self._insufficient(product, rule, agreement_code, "No BOM provided — cannot evaluate Tariff Shift")

        # Determine shift level from rule text or metadata
        shift_level = rule.ts_heading_level or self._infer_shift_level(rule.rule_text)
        ts = evaluate_tariff_shift(
            bom=product.bom,
            output_hs=product.hs_code,
            shift_level=shift_level,
            exceptions=rule.ts_exceptions,
            rule_text=rule.rule_text,
        )
        unknown_origin = sum(1 for b in product.bom if b.is_originating is None)
        confidence = 0.9 if ts.passes and unknown_origin == 0 else (0.65 if unknown_origin > 0 else 0.85)

        return AgreementDetermination(
            agreement_code=agreement_code,
            rule_applied=RuleType.TARIFF_SHIFT,
            rule_text=rule.rule_text,
            result=DeterminationResult.PASS if ts.passes else DeterminationResult.FAIL,
            confidence=confidence,
            reasoning=ts.detail,
            ts_result=ts,
        )

    def _eval_rvc(self, product: ProductInfo, rule: RooRule, agreement_code: str) -> AgreementDetermination:
        if not product.bom:
            return self._insufficient(product, rule, agreement_code, "No BOM provided — cannot evaluate RVC")
        if product.transaction_value_usd <= 0:
            return self._insufficient(product, rule, agreement_code, "Transaction value not set")

        threshold = rule.value_threshold or 40.0
        method = rule.rvc_method or self._infer_rvc_method(rule.rule_type)

        if method == "build_down":
            rvc = calculate_build_down(product.bom, product.transaction_value_usd, threshold)
        elif method == "build_up":
            rvc = calculate_build_up(product.bom, product.transaction_value_usd, threshold)
        elif method == "net_cost":
            if product.net_cost_usd is None:
                return self._insufficient(product, rule, agreement_code, "Net cost not provided for Net Cost RVC method")
            rvc = calculate_net_cost(product.bom, product.transaction_value_usd, product.net_cost_usd, threshold)
        else:
            rvc = best_rvc_method(product.bom, product.transaction_value_usd, threshold, product.net_cost_usd)

        unknown = sum(1 for b in product.bom if b.is_originating is None)
        confidence = 0.92 if rvc.passes and unknown == 0 else (0.6 if unknown > 2 else 0.75)

        return AgreementDetermination(
            agreement_code=agreement_code,
            rule_applied=rule.rule_type,
            rule_text=rule.rule_text,
            result=DeterminationResult.PASS if rvc.passes else DeterminationResult.FAIL,
            confidence=confidence,
            reasoning=rvc.calculation_detail,
            rvc_result=rvc,
        )

    def _eval_combined(self, product: ProductInfo, rule: RooRule, agreement_code: str) -> AgreementDetermination:
        """Evaluate a combined rule (Tariff Shift AND RVC must both pass)."""
        ts_det = self._eval_tariff_shift(product, rule, agreement_code)
        rvc_det = self._eval_rvc(product, rule, agreement_code) if rule.secondary_rule else None

        both_pass = (
            ts_det.result == DeterminationResult.PASS
            and (rvc_det is None or rvc_det.result == DeterminationResult.PASS)
        )
        confidence = min(ts_det.confidence, rvc_det.confidence if rvc_det else 1.0)
        reasoning = f"Combined rule:\n  TS: {ts_det.reasoning}"
        if rvc_det:
            reasoning += f"\n  RVC: {rvc_det.reasoning}"

        return AgreementDetermination(
            agreement_code=agreement_code,
            rule_applied=RuleType.COMBINED,
            rule_text=rule.rule_text,
            result=DeterminationResult.PASS if both_pass else DeterminationResult.FAIL,
            confidence=confidence,
            reasoning=reasoning,
            ts_result=ts_det.ts_result,
            rvc_result=rvc_det.rvc_result if rvc_det else None,
        )

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _insufficient(self, product: ProductInfo, rule: RooRule, agreement_code: str, reason: str) -> AgreementDetermination:
        return AgreementDetermination(
            agreement_code=agreement_code,
            rule_applied=rule.rule_type,
            rule_text=rule.rule_text,
            result=DeterminationResult.INSUFFICIENT_DATA,
            confidence=0.0,
            reasoning=f"Insufficient data: {reason}",
        )

    def _infer_shift_level(self, rule_text: str) -> str:
        text = rule_text.upper()
        if "CTSH" in text or "SUB-HEADING" in text or "SUBHEADING" in text:
            return "subheading"
        if "CTH" in text or "HEADING" in text:
            return "heading"
        return "chapter"

    def _infer_rvc_method(self, rule_type: RuleType) -> str:
        mapping = {
            RuleType.RVC_BUILD_DOWN: "build_down",
            RuleType.RVC_BUILD_UP: "build_up",
            RuleType.RVC_NET_COST: "net_cost",
        }
        return mapping.get(rule_type, "build_down")

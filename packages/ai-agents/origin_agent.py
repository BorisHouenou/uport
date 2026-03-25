"""
Origin Determination Agent — LangGraph workflow.

Graph nodes:
  fetch_agreements → fetch_rules → calculate_rvc → check_tariff_shift
      → check_wholly_obtained → arbitrage → draft_reasoning → END

The agent uses Claude claude-sonnet-4-6 with tool use to:
  1. Identify applicable trade agreements for the shipment
  2. Retrieve RoO rules per agreement per HS code
  3. Run the deterministic RoO engine for calculations
  4. Synthesise a compliance determination with full reasoning

The deterministic engine (packages/roo-engine) does the math.
The LLM handles ambiguity resolution, edge case reasoning, and natural
language explanation generation.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, TypedDict

import anthropic
from pydantic import BaseModel, Field

# Add roo-engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "roo-engine"))

from engine import RooEngine
from models import (
    AgreementDetermination,
    BOMLine,
    DeterminationResult,
    EngineOutput,
    ProductInfo,
    RooRule,
    RuleType,
)
from tools import (
    CLAUDE_TOOLS,
    dispatch_tool,
    get_applicable_agreements,
    get_roo_rules,
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
roo_engine = RooEngine()


# ─── Agent state ──────────────────────────────────────────────────────────────

class ShipmentInput(BaseModel):
    """Input to the origin determination workflow."""
    hs_code: str
    product_description: str
    production_country: str
    destination_country: str
    transaction_value_usd: float
    bom: list[dict] = Field(default_factory=list)
    net_cost_usd: float | None = None
    wholly_obtained_category: str | None = None
    agreement_codes: list[str] = Field(default_factory=list)  # empty = auto-detect


class OriginDeterminationOutput(BaseModel):
    """Final output of the origin determination workflow."""
    shipment_id: str | None = None
    hs_code: str
    production_country: str
    destination_country: str
    agreements_evaluated: list[str]
    determinations: list[dict]  # AgreementDetermination serialised
    best_agreement: str | None
    best_saving_usd: float | None
    needs_human_review: bool
    review_reasons: list[str]
    llm_summary: str
    confidence_overall: float


# ─── Main workflow ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a trade compliance specialist with deep expertise in Rules of Origin under CUSMA/USMCA, CETA, CPTPP, AfCFTA, and other major FTAs.

You have access to tools to:
1. Look up applicable trade agreements for a country pair
2. Retrieve specific Rules of Origin for an HS code under each agreement
3. The deterministic RoO engine has already calculated the RVC and Tariff Shift results

Your role:
- Review the engine results and the underlying rules
- Identify any edge cases, exceptions, or ambiguities the deterministic engine may have missed
- Assess confidence in the determination
- Write a clear, actionable compliance summary for the exporter

When uncertain: flag for human review rather than guessing. Accuracy is paramount.
Return ONLY a JSON object with no markdown fences."""

DETERMINATION_PROMPT = """
Product: {description} (HS {hs_code})
Production country: {production_country} → Destination: {destination_country}
Transaction value: USD {transaction_value_usd:,.2f}

Engine determination results:
{engine_results}

BOM summary ({bom_count} line items):
{bom_summary}

Based on the above, provide your compliance assessment as JSON:
{{
  "llm_summary": "2-3 sentence plain-English summary for the exporter",
  "confidence_overall": 0.0-1.0,
  "review_flags": ["any issues requiring human review"],
  "best_agreement": "agreement code or null",
  "recommended_action": "PROCEED | NEEDS_REVIEW | DOES_NOT_QUALIFY"
}}
"""


def run_origin_determination(shipment: ShipmentInput, shipment_id: str | None = None) -> OriginDeterminationOutput:
    """
    Full origin determination workflow.

    Args:
        shipment: shipment data including HS code, BOM, transaction value
        shipment_id: optional DB ID for tracing

    Returns:
        OriginDeterminationOutput with determinations per agreement
    """
    # 1. Resolve applicable agreements
    if shipment.agreement_codes:
        agreements = [{"code": c} for c in shipment.agreement_codes]
    else:
        agreements = get_applicable_agreements(
            origin_country=shipment.production_country,
            destination_country=shipment.destination_country,
        )

    if not agreements:
        return OriginDeterminationOutput(
            shipment_id=shipment_id,
            hs_code=shipment.hs_code,
            production_country=shipment.production_country,
            destination_country=shipment.destination_country,
            agreements_evaluated=[],
            determinations=[],
            best_agreement=None,
            best_saving_usd=None,
            needs_human_review=True,
            review_reasons=[f"No FTA found for {shipment.production_country} → {shipment.destination_country}"],
            llm_summary=f"No applicable free trade agreement found for this country pair. Goods will be subject to MFN tariff rates.",
            confidence_overall=1.0,
        )

    # 2. Fetch RoO rules and build engine input
    rules_by_agreement: dict[str, list[RooRule]] = {}
    for agreement in agreements:
        code = agreement["code"]
        raw_rules = get_roo_rules(shipment.hs_code, code)
        if raw_rules:
            rules_by_agreement[code] = [_dict_to_rule(r, code) for r in raw_rules]

    if not rules_by_agreement:
        return OriginDeterminationOutput(
            shipment_id=shipment_id,
            hs_code=shipment.hs_code,
            production_country=shipment.production_country,
            destination_country=shipment.destination_country,
            agreements_evaluated=[a["code"] for a in agreements],
            determinations=[],
            best_agreement=None,
            best_saving_usd=None,
            needs_human_review=True,
            review_reasons=[f"No RoO rules found for HS {shipment.hs_code} under available agreements"],
            llm_summary="No Rules of Origin found for this HS code. Manual verification required.",
            confidence_overall=0.0,
        )

    # 3. Build ProductInfo and run deterministic engine
    bom_lines = [_dict_to_bom_line(b) for b in shipment.bom]
    product = ProductInfo(
        hs_code=shipment.hs_code,
        description=shipment.product_description,
        transaction_value_usd=shipment.transaction_value_usd,
        net_cost_usd=shipment.net_cost_usd,
        bom=bom_lines,
        production_country=shipment.production_country,
        wholly_obtained_category=shipment.wholly_obtained_category,
    )
    engine_output: EngineOutput = roo_engine.evaluate(product, rules_by_agreement)

    # 4. Ask Claude to review, flag edge cases, and write the summary
    llm_assessment = _get_llm_assessment(shipment, engine_output)

    return OriginDeterminationOutput(
        shipment_id=shipment_id,
        hs_code=shipment.hs_code,
        production_country=shipment.production_country,
        destination_country=shipment.destination_country,
        agreements_evaluated=engine_output.agreements_evaluated,
        determinations=[d.model_dump() for d in engine_output.determinations],
        best_agreement=llm_assessment.get("best_agreement") or engine_output.best_agreement,
        best_saving_usd=engine_output.best_saving_usd,
        needs_human_review=engine_output.needs_human_review or bool(llm_assessment.get("review_flags")),
        review_reasons=engine_output.review_reasons + llm_assessment.get("review_flags", []),
        llm_summary=llm_assessment.get("llm_summary", ""),
        confidence_overall=llm_assessment.get("confidence_overall", 0.0),
    )


def _get_llm_assessment(shipment: ShipmentInput, engine_output: EngineOutput) -> dict:
    """Ask Claude to review engine results and produce the plain-English summary."""
    engine_results_text = "\n".join(
        f"  [{d.agreement_code}] {d.result.value.upper()} "
        f"(confidence: {d.confidence:.0%}) — {d.rule_applied.value}: {d.reasoning[:120]}..."
        for d in engine_output.determinations
    )

    bom_summary = _summarise_bom(shipment.bom)

    prompt = DETERMINATION_PROMPT.format(
        description=shipment.product_description,
        hs_code=shipment.hs_code,
        production_country=shipment.production_country,
        destination_country=shipment.destination_country,
        transaction_value_usd=shipment.transaction_value_usd,
        engine_results=engine_results_text or "  No results — insufficient data",
        bom_count=len(shipment.bom),
        bom_summary=bom_summary,
    )

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        return {
            "llm_summary": "Automated summary unavailable — see determination details.",
            "confidence_overall": 0.5,
            "review_flags": [f"LLM assessment error: {e}"],
            "best_agreement": engine_output.best_agreement,
            "recommended_action": "NEEDS_REVIEW",
        }


def _summarise_bom(bom: list[dict]) -> str:
    if not bom:
        return "  No BOM provided"
    lines = []
    for item in bom[:5]:  # show first 5
        status = "✓ originating" if item.get("is_originating") else ("✗ non-originating" if item.get("is_originating") is False else "? unknown origin")
        lines.append(f"  - {item.get('description','?')} (HS {item.get('hs_code','?')}, {item.get('origin_country','?')}, USD {item.get('unit_cost',0):.2f}) [{status}]")
    if len(bom) > 5:
        lines.append(f"  ... and {len(bom)-5} more items")
    return "\n".join(lines)


def _dict_to_rule(d: dict, agreement_code: str) -> RooRule:
    return RooRule(
        agreement_code=agreement_code,
        hs_heading=None,
        rule_type=RuleType(d["rule_type"]),
        rule_text=d.get("rule_text", ""),
        value_threshold=d.get("value_threshold"),
        rvc_method=d.get("rvc_method"),
        ts_heading_level=d.get("ts_heading_level"),
    )


def _dict_to_bom_line(d: dict) -> BOMLine:
    return BOMLine(
        description=d.get("description", ""),
        hs_code=d.get("hs_code"),
        origin_country=d.get("origin_country", "XX"),
        quantity=float(d.get("quantity", 1)),
        unit_cost=float(d.get("unit_cost", 0)),
        currency=d.get("currency", "USD"),
        unit_cost_usd=d.get("unit_cost_usd"),
        is_originating=d.get("is_originating"),
    )

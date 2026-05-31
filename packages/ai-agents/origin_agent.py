"""
Origin Determination Agent — agentic tool-calling loop.

Architecture
------------
Claude (claude-sonnet-4-6) drives the workflow via tool use, calling:
  1. get_applicable_agreements  — which FTAs apply to this country pair?
  2. get_roo_rules              — what rule governs this HS code under each FTA?
  3. run_roo_engine             — execute the deterministic RVC/TS/WO calculations
  4. get_tariff_rates           — what tariff savings does preferential origin unlock?

The deterministic engine (packages/roo-engine) does the math; Claude handles
ambiguity resolution, edge case reasoning, and plain-language summarisation.

The loop runs up to MAX_TOOL_ROUNDS iterations, mirroring the hs_classifier pattern.
Claude decides when it has enough information to produce the final JSON determination.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

import anthropic
from pydantic import BaseModel, Field

# Add roo-engine to path so engine models are importable directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "roo-engine"))

from tools import CLAUDE_TOOLS, dispatch_tool

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
MAX_TOOL_ROUNDS = 10
MAX_TOKENS = 2048


# ─── Input / output models ─────────────────────────────────────────────────────

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
    determinations: list[dict]
    best_agreement: str | None
    best_saving_usd: float | None
    needs_human_review: bool
    review_reasons: list[str]
    llm_summary: str
    confidence_overall: float
    recommended_action: str  # PROCEED | NEEDS_REVIEW | DOES_NOT_QUALIFY
    tool_calls_made: int = 0


# ─── Prompts ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a trade compliance specialist with deep expertise in Rules of Origin under CUSMA/USMCA, CETA, CPTPP, AfCFTA, and other major FTAs.

You have access to tools to analyse shipments:
- get_applicable_agreements: find which FTAs cover this country pair
- get_roo_rules: retrieve the PSR (Product-Specific Rule) for the HS code under each FTA
- run_roo_engine: execute the deterministic RVC / Tariff Shift / Wholly Obtained calculations
- get_tariff_rates: look up the MFN tariff rate and potential preferential rate savings

Workflow:
1. Call get_applicable_agreements to discover relevant FTAs
2. Call get_roo_rules for each FTA to understand what rule governs this product
3. Call run_roo_engine to get the deterministic calculation results
4. Optionally call get_tariff_rates to quantify savings
5. Synthesise everything into a structured JSON determination

Important principles:
- Run the engine (run_roo_engine) before writing your final determination — never guess at RVC numbers
- If get_roo_rules returns no rules, flag for human review; do not fabricate a rule
- When BOM lines have unknown origin (is_originating: null), note this reduces confidence
- AfCFTA uses Build-Up (value added content) ≥35%; CUSMA/CETA/CPTPP use Build-Down or Net Cost
- Confidence should reflect: how specific the rule match was, how complete the BOM data is, and whether the engine produced a clear pass or fail

When you have a complete determination, return ONLY a JSON object (no markdown fences):
{
  "agreements_evaluated": ["cusma", "ceta"],
  "determinations": [...engine output determinations...],
  "best_agreement": "cusma" or null,
  "best_saving_usd": 1234.56 or null,
  "needs_human_review": true/false,
  "review_reasons": ["reason if any"],
  "llm_summary": "2-3 sentence plain-English explanation for the exporter",
  "confidence_overall": 0.0-1.0,
  "recommended_action": "PROCEED" | "NEEDS_REVIEW" | "DOES_NOT_QUALIFY"
}"""


def _make_user_message(shipment: ShipmentInput) -> str:
    bom_lines = shipment.bom[:10]
    bom_text = "\n".join(
        f"  - {b.get('description', '?')} | HS {b.get('hs_code', '?')} | "
        f"{b.get('origin_country', '?')} | USD {b.get('unit_cost', 0):.2f} × {b.get('quantity', 1)} | "
        f"originating: {b.get('is_originating', 'unknown')}"
        for b in bom_lines
    )
    if len(shipment.bom) > 10:
        bom_text += f"\n  ... and {len(shipment.bom) - 10} more items"

    return f"""Determine Rules of Origin compliance for this shipment:

Product: {shipment.product_description} (HS {shipment.hs_code})
Production country: {shipment.production_country}
Destination: {shipment.destination_country}
Transaction value: USD {shipment.transaction_value_usd:,.2f}
Net cost: {f'USD {shipment.net_cost_usd:,.2f}' if shipment.net_cost_usd else 'not provided'}
Wholly obtained category: {shipment.wholly_obtained_category or 'N/A'}
FTAs to evaluate: {', '.join(shipment.agreement_codes) if shipment.agreement_codes else 'auto-detect'}

BOM ({len(shipment.bom)} items):
{bom_text or '  (no BOM provided)'}

Use the available tools to run the complete origin determination and return the structured JSON result."""


# ─── Main agentic loop ─────────────────────────────────────────────────────────

def run_origin_determination(
    shipment: ShipmentInput,
    shipment_id: str | None = None,
) -> OriginDeterminationOutput:
    """
    Run the full origin determination via agentic tool loop.

    Claude calls tools iteratively until it has enough information to produce
    a complete structured determination. The loop mirrors hs_classifier.py.
    """
    messages: list[dict] = [{"role": "user", "content": _make_user_message(shipment)}]
    tool_calls_made = 0

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=CLAUDE_TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text") and block.text.strip():
                    return _parse_result(block.text, shipment, shipment_id, tool_calls_made)
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls_made += 1
                    try:
                        result = dispatch_tool(block.name, block.input)
                    except Exception as exc:
                        result = {"error": str(exc)}
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, default=str),
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    # Fallback: no clean JSON from Claude — return needs_review
    return OriginDeterminationOutput(
        shipment_id=shipment_id,
        hs_code=shipment.hs_code,
        production_country=shipment.production_country,
        destination_country=shipment.destination_country,
        agreements_evaluated=shipment.agreement_codes or [],
        determinations=[],
        best_agreement=None,
        best_saving_usd=None,
        needs_human_review=True,
        review_reasons=["Agent did not produce a structured determination within allowed rounds"],
        llm_summary="Automated determination incomplete — manual review required.",
        confidence_overall=0.0,
        recommended_action="NEEDS_REVIEW",
        tool_calls_made=tool_calls_made,
    )


def _parse_result(
    text: str,
    shipment: ShipmentInput,
    shipment_id: str | None,
    tool_calls_made: int,
) -> OriginDeterminationOutput:
    """Parse Claude's final JSON output into OriginDeterminationOutput."""
    text = text.strip()
    # Strip markdown fences
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    try:
        data = json.loads(text)
        return OriginDeterminationOutput(
            shipment_id=shipment_id,
            hs_code=shipment.hs_code,
            production_country=shipment.production_country,
            destination_country=shipment.destination_country,
            agreements_evaluated=data.get("agreements_evaluated", []),
            determinations=data.get("determinations", []),
            best_agreement=data.get("best_agreement"),
            best_saving_usd=data.get("best_saving_usd"),
            needs_human_review=bool(data.get("needs_human_review", False)),
            review_reasons=data.get("review_reasons", []),
            llm_summary=data.get("llm_summary", ""),
            confidence_overall=float(data.get("confidence_overall", 0.0)),
            recommended_action=data.get("recommended_action", "NEEDS_REVIEW"),
            tool_calls_made=tool_calls_made,
        )
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
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
            review_reasons=[f"Failed to parse agent output: {exc}"],
            llm_summary="Parse error in agent output — manual review required.",
            confidence_overall=0.0,
            recommended_action="NEEDS_REVIEW",
            tool_calls_made=tool_calls_made,
        )

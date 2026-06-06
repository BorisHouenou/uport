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
import logging
import os
import re
import sys
from typing import Any

import anthropic
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Add roo-engine to path so engine models are importable directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "roo-engine"))

from tools import CLAUDE_TOOLS, dispatch_tool

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
MAX_TOOL_ROUNDS = 15
MAX_TOKENS = 4096


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

    hs_note = ""
    if not shipment.hs_code or shipment.hs_code in ("0000", "0000.00"):
        hs_note = (
            "\n\nIMPORTANT: The HS code for this finished good has not been set (shown as 0000). "
            "You MUST call search_tariff_schedule using the product name to identify the correct "
            "HS code for the FINISHED GOOD before calling get_roo_rules or run_roo_engine. "
            "The BOM items listed are COMPONENTS/INPUTS — their HS codes are NOT the finished-good HS. "
            "The finished-good HS is the tariff classification of the assembled product itself."
        )

    return f"""Determine Rules of Origin compliance for this shipment:

Product: {shipment.product_description} (HS {shipment.hs_code}){hs_note}
Production country: {shipment.production_country}
Destination: {shipment.destination_country}
Transaction value: USD {shipment.transaction_value_usd:,.2f}
Net cost: {f'USD {shipment.net_cost_usd:,.2f}' if shipment.net_cost_usd else 'not provided'}
Wholly obtained category: {shipment.wholly_obtained_category or 'N/A'}
FTAs to evaluate: {', '.join(shipment.agreement_codes) if shipment.agreement_codes else 'auto-detect'}

BOM ({len(shipment.bom)} items — these are INPUT COMPONENTS, not the finished good):
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


def _bracket_extract(text: str) -> str:
    """Return the first complete JSON object from text via bracket counting."""
    start = text.find('{')
    if start == -1:
        return text
    depth = 0
    in_string = False
    escape_next = False
    for i, ch in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue
        if ch == '\\' and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return text[start:]  # truncated — let json.loads produce a clear error


def _extract_json_object(text: str) -> str:
    """
    Extract the first complete JSON object from text.
    Handles markdown fences anywhere in the text and bare JSON with surrounding prose.
    """
    # Look for a fenced block (with or without preamble before the fence)
    fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if fence_match:
        # Run bracket extraction on the fenced content (may itself have prose)
        return _bracket_extract(fence_match.group(1).strip())

    # No fence — bracket-match directly in the full text
    return _bracket_extract(text)


def _parse_result(
    text: str,
    shipment: ShipmentInput,
    shipment_id: str | None,
    tool_calls_made: int,
) -> OriginDeterminationOutput:
    """Parse Claude's final JSON output into OriginDeterminationOutput."""
    raw = text.strip()
    logger.info("Origin agent raw output (%d chars): %.500s", len(raw), raw)

    try:
        candidate = _extract_json_object(raw)
        data = json.loads(candidate)
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
        logger.warning(
            "Failed to parse origin agent output: %s\nFull text: %s", exc, raw
        )
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

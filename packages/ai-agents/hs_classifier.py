"""
HS Code Classification Agent.

Uses Claude claude-sonnet-4-6 with tool_use to classify products into HS codes.
Returns structured output: hs_code, confidence, alternatives, reasoning.

Flow:
  1. Claude receives product description
  2. Calls search_tariff_schedule to find candidates
  3. Calls validate_hs_code to confirm the best match
  4. Returns structured HSClassificationResult
"""
from __future__ import annotations

import json
import os
from typing import Any

import anthropic
from pydantic import BaseModel, Field

from tools import CLAUDE_TOOLS, dispatch_tool

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 1024
MAX_TOOL_ROUNDS = 5


class HSAlternative(BaseModel):
    hs_code: str
    description: str
    confidence: float
    reason: str


class HSClassificationResult(BaseModel):
    hs_code: str
    hs_description: str
    chapter: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    alternatives: list[HSAlternative] = Field(default_factory=list)
    tool_calls_made: int = 0


SYSTEM_PROMPT = """You are an expert customs tariff classifier specialising in the Harmonised System (HS) nomenclature.

Your task: classify a product into the most accurate HS code using the tools available.

Rules:
1. ALWAYS use search_tariff_schedule first to find candidate HS codes
2. Use validate_hs_code to confirm your top pick
3. Return a JSON object with EXACTLY this structure (no markdown, raw JSON only):
{
  "hs_code": "XXXXXXXX",
  "hs_description": "Official description from the tariff schedule",
  "chapter": "XX",
  "confidence": 0.0-1.0,
  "reasoning": "Explain why this code was selected",
  "alternatives": [
    {"hs_code": "...", "description": "...", "confidence": 0.0-1.0, "reason": "..."}
  ]
}

Confidence guide:
- 0.95+: Exact match, unambiguous product description
- 0.80-0.94: Strong match, minor ambiguity
- 0.60-0.79: Probable match, product needs more details
- <0.60: Uncertain — flag for human review

Consider: is the product a finished good, part, or raw material? Is it for personal or industrial use?"""


def classify(description: str, additional_context: str = "") -> HSClassificationResult:
    """
    Classify a product description into an HS code using Claude + tool use.

    Args:
        description: product description (required)
        additional_context: optional additional context (e.g. "used in automotive assembly")

    Returns:
        HSClassificationResult with hs_code, confidence, alternatives
    """
    user_content = description
    if additional_context:
        user_content += f"\n\nAdditional context: {additional_context}"

    messages: list[dict] = [{"role": "user", "content": user_content}]
    tool_calls_made = 0

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=CLAUDE_TOOLS[:2],  # HS classifier only needs search + validate tools
            messages=messages,
        )

        # Append assistant response to conversation
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Extract JSON from the final text block
            for block in response.content:
                if hasattr(block, "text"):
                    return _parse_result(block.text, tool_calls_made)
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls_made += 1
                    result = dispatch_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    # Fallback: return low-confidence result
    return HSClassificationResult(
        hs_code="0000.00",
        hs_description="Classification failed — insufficient data",
        chapter="00",
        confidence=0.0,
        reasoning="Agent could not complete classification within allowed rounds",
        tool_calls_made=tool_calls_made,
    )


def _parse_result(text: str, tool_calls_made: int) -> HSClassificationResult:
    """Parse the agent's JSON output into a typed result."""
    # Strip markdown code fences if present
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    try:
        data = json.loads(text)
        alts = [HSAlternative(**a) for a in data.get("alternatives", [])]
        return HSClassificationResult(
            hs_code=data["hs_code"],
            hs_description=data.get("hs_description", ""),
            chapter=data.get("chapter", data["hs_code"][:2]),
            confidence=float(data.get("confidence", 0.5)),
            reasoning=data.get("reasoning", ""),
            alternatives=alts,
            tool_calls_made=tool_calls_made,
        )
    except (json.JSONDecodeError, KeyError) as e:
        return HSClassificationResult(
            hs_code="0000.00",
            hs_description="Parse error",
            chapter="00",
            confidence=0.0,
            reasoning=f"Failed to parse agent output: {e}\nRaw: {text[:200]}",
            tool_calls_made=tool_calls_made,
        )


def classify_batch(items: list[dict]) -> list[HSClassificationResult]:
    """
    Classify multiple BOM line items.
    items: list of {"description": str, "context": str (optional)}
    """
    return [
        classify(item["description"], item.get("context", ""))
        for item in items
    ]

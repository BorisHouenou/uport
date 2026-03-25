"""
Tool definitions for Uportai AI agents.

All tools are pure functions — no side effects except DB reads.
They are registered as Claude tool_use schemas and as LangGraph ToolNodes.
"""
from __future__ import annotations

import json
from typing import Any

# ─── Harmonised System tariff schedule (abbreviated for bootstrapping) ────────
# Full schedule loaded from data/trade-agreements/ at runtime
HS_SCHEDULE: dict[str, dict] = {
    # Chapter 01 — Live animals
    "0101": {"description": "Live horses, asses, mules and hinnies", "chapter": "01"},
    "0102": {"description": "Live bovine animals", "chapter": "01"},
    # Chapter 08 — Edible fruit and nuts
    "0801": {"description": "Coconuts, Brazil nuts and cashew nuts, fresh or dried", "chapter": "08"},
    # Chapter 61 — Knitted apparel
    "6101": {"description": "Men's or boys' overcoats, cardigans (knitted)", "chapter": "61"},
    "6104": {"description": "Women's suits, knitted or crocheted", "chapter": "61"},
    # Chapter 73 — Iron/steel articles
    "7318": {"description": "Screws, bolts, nuts, washers of iron or steel", "chapter": "73"},
    "7326": {"description": "Other articles of iron or steel", "chapter": "73"},
    # Chapter 84 — Machinery
    "8401": {"description": "Nuclear reactors, fuel elements, isotope separators", "chapter": "84"},
    "8471": {"description": "Automatic data processing machines (computers)", "chapter": "84"},
    "8479": {"description": "Machines/mechanical appliances not elsewhere specified", "chapter": "84"},
    # Chapter 85 — Electrical machinery
    "8517": {"description": "Telephone sets, smartphones, communication devices", "chapter": "85"},
    "8528": {"description": "Monitors, projectors, TV receivers", "chapter": "85"},
    "8544": {"description": "Insulated wire, cable, optical fibre cables", "chapter": "85"},
    # Chapter 87 — Vehicles
    "8703": {"description": "Motor cars and other motor vehicles for persons", "chapter": "87"},
    "8704": {"description": "Motor vehicles for transport of goods", "chapter": "87"},
    "8708": {"description": "Parts and accessories for motor vehicles", "chapter": "87"},
    # Chapter 90 — Optical, measuring instruments
    "9013": {"description": "Liquid crystal devices, lasers, optical appliances", "chapter": "90"},
    "9021": {"description": "Orthopaedic appliances, splints, hearing aids", "chapter": "90"},
}


def search_tariff_schedule(description: str, max_results: int = 5) -> list[dict]:
    """
    Search the HS tariff schedule for codes matching a product description.
    Returns list of {hs_code, description, chapter} sorted by relevance.

    In production: queries the hs_codes table with pg_trgm similarity search.
    In bootstrap: keyword match against the abbreviated schedule above.
    """
    desc_lower = description.lower()
    keywords = [w for w in desc_lower.split() if len(w) > 3]

    scored: list[tuple[int, str, dict]] = []
    for code, info in HS_SCHEDULE.items():
        info_lower = info["description"].lower()
        score = sum(1 for kw in keywords if kw in info_lower)
        if score > 0:
            scored.append((score, code, info))

    scored.sort(key=lambda x: -x[0])
    return [
        {"hs_code": code, "description": info["description"], "chapter": info["chapter"], "relevance_score": score}
        for score, code, info in scored[:max_results]
    ]


def validate_hs_code(hs_code: str, country: str = "CA") -> dict:
    """
    Validate that an HS code is structurally valid and exists in the schedule.
    Returns {valid, hs_code, description, chapter, notes}.
    """
    import re
    cleaned = re.sub(r"[.\s]", "", hs_code)
    if not re.match(r"^\d{4,10}$", cleaned):
        return {"valid": False, "hs_code": hs_code, "notes": "HS code must be 4–10 digits"}

    heading = cleaned[:4]
    if heading in HS_SCHEDULE:
        info = HS_SCHEDULE[heading]
        return {
            "valid": True,
            "hs_code": cleaned,
            "description": info["description"],
            "chapter": info["chapter"],
            "notes": "Validated against tariff schedule",
        }
    return {
        "valid": True,  # structurally valid even if not in abbreviated schedule
        "hs_code": cleaned,
        "description": "Description not available in local schedule — verify against full CAN tariff",
        "chapter": cleaned[:2],
        "notes": "Not found in local schedule; likely valid — verify at cbsa-asfc.gc.ca",
    }


def get_applicable_agreements(origin_country: str, destination_country: str) -> list[dict]:
    """
    Return trade agreements applicable to the origin → destination country pair.
    In production: queries the trade_agreements table.
    """
    # Bilateral FTA map (Canada-centric for Phase 1)
    FTA_MAP: dict[tuple[str, str], list[dict]] = {
        ("CA", "US"): [{"code": "cusma", "name": "CUSMA/USMCA", "parties": ["CA", "US", "MX"]}],
        ("CA", "MX"): [{"code": "cusma", "name": "CUSMA/USMCA", "parties": ["CA", "US", "MX"]}],
        ("CA", "DE"): [{"code": "ceta",  "name": "CETA",         "parties": ["CA"] + ["EU"]}],
        ("CA", "FR"): [{"code": "ceta",  "name": "CETA",         "parties": ["CA"] + ["EU"]}],
        ("CA", "GB"): [{"code": "ceta",  "name": "CETA",         "parties": ["CA"] + ["EU"]}],
        ("CA", "JP"): [{"code": "cptpp", "name": "CPTPP",        "parties": ["CA", "JP", "AU", "NZ", "SG", "VN", "MX", "CL", "PE", "MY", "BN"]}],
        ("CA", "AU"): [{"code": "cptpp", "name": "CPTPP",        "parties": ["CA", "JP", "AU", "NZ", "SG", "VN", "MX", "CL", "PE", "MY", "BN"]}],
    }
    key = (origin_country.upper(), destination_country.upper())
    return FTA_MAP.get(key, [])


def get_roo_rules(hs_code: str, agreement_code: str) -> list[dict]:
    """
    Fetch RoO rules for an HS code under a given agreement.
    In production: queries the roo_rules table with hs_heading match.
    """
    import re
    heading = re.sub(r"[.\s]", "", hs_code)[:4]

    # Representative rules for bootstrapping (sourced from official FTA schedules)
    RULES: dict[str, dict[str, list[dict]]] = {
        "cusma": {
            "8703": [{"rule_type": "rvc_build_down", "rule_text": "A change to a heading of 87.03 from any other heading; or No change in tariff classification required, provided there is a regional value content of not less than: (a) 75 percent where the transaction value method is used, or (b) 65 percent where the net cost method is used.", "value_threshold": 75.0, "rvc_method": "build_down"}],
            "8471": [{"rule_type": "tariff_shift",   "rule_text": "CTH — A change to heading 84.71 from any other heading.", "ts_heading_level": "heading"}],
            "8517": [{"rule_type": "rvc_build_down", "rule_text": "RVC not less than 40% (Build-Down)", "value_threshold": 40.0, "rvc_method": "build_down"}],
            "6101": [{"rule_type": "tariff_shift",   "rule_text": "CC — A change to Chapter 61 from any other chapter, except from headings 51.06 through 51.13, 52.04 through 52.12, 53.07 through 53.08 or 53.10 through 53.11.", "ts_heading_level": "chapter"}],
            "7318": [{"rule_type": "rvc_build_down", "rule_text": "RVC not less than 40% (Build-Down)", "value_threshold": 40.0, "rvc_method": "build_down"}],
            "0101": [{"rule_type": "wholly_obtained", "rule_text": "Wholly obtained or produced entirely in the territory of one or more of the Parties."}],
        },
        "ceta": {
            "8703": [{"rule_type": "rvc_build_down", "rule_text": "MaxNOM 45% (EXW) — non-originating materials must not exceed 45% of the ex-works price.", "value_threshold": 55.0, "rvc_method": "build_down"}],
            "8517": [{"rule_type": "tariff_shift",   "rule_text": "CTH — Change in tariff heading from any other heading.", "ts_heading_level": "heading"}],
            "6101": [{"rule_type": "tariff_shift",   "rule_text": "CC — Manufacture from yarn.", "ts_heading_level": "chapter"}],
            "0101": [{"rule_type": "wholly_obtained", "rule_text": "Wholly obtained"}],
        },
        "cptpp": {
            "8703": [{"rule_type": "rvc_build_down", "rule_text": "RVC not less than 40% (Build-Down) or 30% (Net Cost)", "value_threshold": 40.0, "rvc_method": "build_down"}],
            "8517": [{"rule_type": "rvc_build_down", "rule_text": "RVC not less than 40%", "value_threshold": 40.0}],
            "0101": [{"rule_type": "wholly_obtained", "rule_text": "Wholly obtained or produced"}],
        },
    }

    agreement_rules = RULES.get(agreement_code.lower(), {})
    return agreement_rules.get(heading, [])


# ─── Claude tool schemas ──────────────────────────────────────────────────────

CLAUDE_TOOLS = [
    {
        "name": "search_tariff_schedule",
        "description": "Search the Harmonised System (HS) tariff schedule for codes matching a product description. Returns candidate HS codes ranked by relevance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Product description to search for"},
                "max_results": {"type": "integer", "default": 5},
            },
            "required": ["description"],
        },
    },
    {
        "name": "validate_hs_code",
        "description": "Validate an HS code and retrieve its official description and chapter.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hs_code": {"type": "string", "description": "The HS code to validate (4–10 digits)"},
                "country": {"type": "string", "default": "CA"},
            },
            "required": ["hs_code"],
        },
    },
    {
        "name": "get_applicable_agreements",
        "description": "Get the list of free trade agreements applicable to an origin/destination country pair.",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin_country": {"type": "string", "description": "ISO-3166 alpha-2 origin country"},
                "destination_country": {"type": "string", "description": "ISO-3166 alpha-2 destination country"},
            },
            "required": ["origin_country", "destination_country"],
        },
    },
    {
        "name": "get_roo_rules",
        "description": "Fetch Rules of Origin for a specific HS code under a given trade agreement.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hs_code": {"type": "string", "description": "HS code (4 or 6 digit)"},
                "agreement_code": {"type": "string", "description": "FTA code e.g. cusma, ceta, cptpp"},
            },
            "required": ["hs_code", "agreement_code"],
        },
    },
]


def dispatch_tool(name: str, inputs: dict) -> Any:
    """Dispatch a tool call by name."""
    dispatch = {
        "search_tariff_schedule": search_tariff_schedule,
        "validate_hs_code": validate_hs_code,
        "get_applicable_agreements": get_applicable_agreements,
        "get_roo_rules": get_roo_rules,
    }
    if name not in dispatch:
        raise ValueError(f"Unknown tool: {name}")
    return dispatch[name](**inputs)

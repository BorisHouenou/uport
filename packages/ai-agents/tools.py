"""
Tool definitions for Uportai AI agents.

Query order:
  1. DB (PostgreSQL via DATABASE_URL) — production path
  2. In-memory BOOTSTRAP data — dev/test fallback when DB is unavailable

All tools are pure functions — no side effects except DB reads.
They are registered as Claude tool_use schemas and as LangGraph ToolNodes.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any


# ─── Bootstrap data (dev fallback) ────────────────────────────────────────────
# Used when DATABASE_URL is not set. Covers enough headings to demonstrate
# the full workflow. The production DB has 3,000+ rules across all 99 chapters.

_BOOTSTRAP_HS: dict[str, dict] = {
    # Agriculture
    "0101": {"description": "Live horses, asses, mules and hinnies", "chapter": "01"},
    "0102": {"description": "Live bovine animals", "chapter": "01"},
    "0801": {"description": "Coconuts, Brazil nuts and cashew nuts", "chapter": "08"},
    "0901": {"description": "Coffee, whether or not roasted or decaffeinated", "chapter": "09"},
    "1006": {"description": "Rice", "chapter": "10"},
    # Chemicals / pharma
    "3004": {"description": "Medicaments, for retail sale", "chapter": "30"},
    # Plastics
    "3901": {"description": "Polymers of ethylene, in primary forms", "chapter": "39"},
    "3926": {"description": "Other articles of plastics", "chapter": "39"},
    # Rubber
    "4011": {"description": "New pneumatic tyres, of rubber", "chapter": "40"},
    # Textiles / apparel
    "5201": {"description": "Cotton, not carded or combed", "chapter": "52"},
    "6101": {"description": "Men's or boys' overcoats, knitted or crocheted", "chapter": "61"},
    "6104": {"description": "Women's suits, knitted or crocheted", "chapter": "61"},
    "6203": {"description": "Men's or boys' suits and trousers", "chapter": "62"},
    # Footwear
    "6403": {"description": "Footwear, leather upper", "chapter": "64"},
    # Metals
    "7208": {"description": "Flat-rolled steel, hot-rolled, ≥600mm width", "chapter": "72"},
    "7318": {"description": "Screws, bolts, nuts, washers of iron or steel", "chapter": "73"},
    "7326": {"description": "Other articles of iron or steel", "chapter": "73"},
    # Machinery
    "8409": {"description": "Parts for engines of 84.07 or 84.08", "chapter": "84"},
    "8418": {"description": "Refrigerators, freezers and refrigerating equipment", "chapter": "84"},
    "8450": {"description": "Household washing machines", "chapter": "84"},
    "8471": {"description": "Automatic data processing machines (computers)", "chapter": "84"},
    "8479": {"description": "Machines/mechanical appliances not elsewhere specified", "chapter": "84"},
    "8481": {"description": "Taps, cocks, valves and similar appliances", "chapter": "84"},
    "8482": {"description": "Ball or roller bearings", "chapter": "84"},
    # Electronics
    "8501": {"description": "Electric motors and generators", "chapter": "85"},
    "8507": {"description": "Electric accumulators (batteries)", "chapter": "85"},
    "8516": {"description": "Electric water heaters, space heating apparatus", "chapter": "85"},
    "8517": {"description": "Telephone sets, smartphones, communication devices", "chapter": "85"},
    "8528": {"description": "Monitors, projectors, TV receivers", "chapter": "85"},
    "8534": {"description": "Printed circuits", "chapter": "85"},
    "8541": {"description": "Semiconductor devices (diodes, transistors)", "chapter": "85"},
    "8542": {"description": "Electronic integrated circuits", "chapter": "85"},
    "8544": {"description": "Insulated wire, cable, optical fibre cables", "chapter": "85"},
    # Vehicles
    "8701": {"description": "Tractors", "chapter": "87"},
    "8702": {"description": "Motor vehicles for 10+ persons", "chapter": "87"},
    "8703": {"description": "Motor cars and other passenger vehicles", "chapter": "87"},
    "8704": {"description": "Motor vehicles for goods transport", "chapter": "87"},
    "8708": {"description": "Parts and accessories of motor vehicles", "chapter": "87"},
    "8711": {"description": "Motorcycles including mopeds", "chapter": "87"},
    # Instruments
    "9013": {"description": "Liquid crystal devices, lasers, other optical appliances", "chapter": "90"},
    "9018": {"description": "Instruments used in medical, surgical or dental sciences", "chapter": "90"},
    "9021": {"description": "Orthopaedic appliances, hearing aids, prostheses", "chapter": "90"},
    # Furniture / misc
    "9403": {"description": "Other furniture and parts thereof", "chapter": "94"},
    "9503": {"description": "Toys, dolls, games", "chapter": "95"},
}

# country pair → list of applicable FTA codes
_BOOTSTRAP_FTA_MAP: dict[tuple[str, str], list[dict]] = {}

def _build_bootstrap_fta_map() -> dict[tuple[str, str], list[dict]]:
    """Build the bilateral FTA map from seed data agreements."""
    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "roo-database"))
        from seed.agreements import AGREEMENTS
        fta_map: dict[tuple[str, str], list[dict]] = {}
        for ag in AGREEMENTS:
            parties = ag["parties"]
            for i, a in enumerate(parties):
                for b in parties:
                    if a != b:
                        key = (a, b)
                        entry = {"code": ag["code"], "name": ag["name"], "parties": parties}
                        if key not in fta_map:
                            fta_map[key] = []
                        if not any(e["code"] == ag["code"] for e in fta_map[key]):
                            fta_map[key].append(entry)
        return fta_map
    except Exception:
        # Hard fallback — CUSMA, CETA (sample), CPTPP (sample)
        EU = ["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
              "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT",
              "NL", "PL", "PT", "RO", "SE", "SI", "SK"]
        CPTPP = ["AU", "BN", "CA", "CL", "JP", "MX", "MY", "NZ", "PE", "SG", "VN"]
        CUSMA = ["CA", "US", "MX"]
        result = {}
        for a in CUSMA:
            for b in CUSMA:
                if a != b:
                    result.setdefault((a, b), []).append(
                        {"code": "cusma", "name": "CUSMA/USMCA", "parties": CUSMA}
                    )
        for eu in EU:
            result.setdefault(("CA", eu), []).append(
                {"code": "ceta", "name": "CETA", "parties": ["CA"] + EU}
            )
            result.setdefault((eu, "CA"), []).append(
                {"code": "ceta", "name": "CETA", "parties": ["CA"] + EU}
            )
        for a in CPTPP:
            for b in CPTPP:
                if a != b:
                    result.setdefault((a, b), []).append(
                        {"code": "cptpp", "name": "CPTPP", "parties": CPTPP}
                    )
        return result


# Bootstrap PSR rules — loaded lazily from seed files
_BOOTSTRAP_RULES: dict[str, dict[str, list[dict]]] | None = None

def _get_bootstrap_rules() -> dict[str, dict[str, list[dict]]]:
    """Build heading → rule lookup from seed PSR data."""
    global _BOOTSTRAP_RULES
    if _BOOTSTRAP_RULES is not None:
        return _BOOTSTRAP_RULES

    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "roo-database"))
        from seed.cusma_psrs import CUSMA_RULES
        from seed.ceta_psrs import CETA_RULES
        from seed.cptpp_psrs import CPTPP_RULES
        from seed.afcfta_psrs import AFCFTA_RULES

        def _index_rules(raw: list[tuple]) -> dict[str, list[dict]]:
            """Index rules by exact hs_code (chapter, heading, or subheading)."""
            idx: dict[str, list[dict]] = {}
            for r in raw:
                (hs_code, rule_type, rule_text, threshold, rvc_method, ts_level,
                 sec_type, sec_threshold, sec_rvc, source_ref, is_default) = r
                entry = {
                    "rule_type": rule_type,
                    "rule_text": rule_text,
                    "value_threshold": threshold,
                    "rvc_method": rvc_method,
                    "ts_heading_level": ts_level,
                    "secondary_rule_type": sec_type,
                    "secondary_value_threshold": sec_threshold,
                    "source_reference": source_ref,
                    "is_default": is_default,
                }
                idx.setdefault(hs_code, []).append(entry)
            return idx

        _BOOTSTRAP_RULES = {
            "cusma":  _index_rules(CUSMA_RULES),
            "ceta":   _index_rules(CETA_RULES),
            "cptpp":  _index_rules(CPTPP_RULES),
            "afcfta": _index_rules(AFCFTA_RULES),
        }
    except Exception:
        _BOOTSTRAP_RULES = {}

    return _BOOTSTRAP_RULES


# ─── DB helpers ───────────────────────────────────────────────────────────────

def _get_sync_conn():
    """Return a synchronous psycopg2/psycopg connection, or None if unavailable."""
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        return None
    try:
        from sqlalchemy import create_engine
        url = db_url.replace("+asyncpg", "")
        engine = create_engine(url, pool_pre_ping=True)
        return engine.connect()
    except Exception:
        return None


def _db_search_hs(description: str, max_results: int = 5) -> list[dict] | None:
    """Search hs_codes table using pg_trgm similarity. Returns None on DB error."""
    conn = _get_sync_conn()
    if not conn:
        return None
    try:
        from sqlalchemy import text
        rows = conn.execute(
            text("""
                SELECT heading, chapter, description,
                       similarity(description, :q) AS score
                FROM hs_codes
                WHERE is_heading = true
                  AND similarity(description, :q) > 0.1
                ORDER BY score DESC
                LIMIT :limit
            """),
            {"q": description, "limit": max_results},
        ).fetchall()
        return [
            {"hs_code": r[0], "chapter": r[1],
             "description": r[2], "relevance_score": float(r[3])}
            for r in rows
        ]
    except Exception:
        return None
    finally:
        conn.close()


def _db_get_applicable_agreements(origin: str, destination: str) -> list[dict] | None:
    """Query trade_agreements where both countries are in parties array."""
    conn = _get_sync_conn()
    if not conn:
        return None
    try:
        from sqlalchemy import text
        rows = conn.execute(
            text("""
                SELECT code, name, parties
                FROM trade_agreements
                WHERE is_active = true
                  AND parties @> ARRAY[:origin]::varchar[]
                  AND parties @> ARRAY[:dest]::varchar[]
                ORDER BY effective_date ASC
            """),
            {"origin": origin.upper(), "dest": destination.upper()},
        ).fetchall()
        return [
            {"code": r[0], "name": r[1], "parties": list(r[2])}
            for r in rows
        ]
    except Exception:
        return None
    finally:
        conn.close()


def _db_get_roo_rules(hs_code: str, agreement_code: str) -> list[dict] | None:
    """
    Fetch RoO rules from DB with 3-level fallback:
    1. Exact subheading (6-digit)
    2. Heading (4-digit)
    3. Chapter default (2-digit, is_default=true)
    """
    conn = _get_sync_conn()
    if not conn:
        return None
    try:
        from sqlalchemy import text
        cleaned = re.sub(r"[.\s]", "", hs_code)
        heading = cleaned[:4]
        chapter = cleaned[:2]
        subheading = cleaned[:6] if len(cleaned) >= 6 else None

        rows = conn.execute(
            text("""
                WITH ag AS (
                    SELECT id FROM trade_agreements WHERE code = :code LIMIT 1
                )
                SELECT r.rule_type, r.rule_text, r.value_threshold,
                       r.rvc_method, r.ts_heading_level, r.ts_exceptions,
                       r.secondary_rule_type, r.secondary_value_threshold,
                       r.secondary_rvc_method, r.source_reference,
                       r.hs_subheading, r.hs_heading, r.hs_chapter, r.is_default
                FROM roo_rules r
                JOIN ag ON r.agreement_id = ag.id
                WHERE (
                    (:subheading IS NOT NULL AND r.hs_subheading = :subheading)
                    OR r.hs_heading = :heading
                    OR (r.hs_chapter = :chapter AND r.is_default = true)
                )
                ORDER BY
                    CASE
                        WHEN r.hs_subheading IS NOT NULL AND r.hs_subheading = :subheading THEN 1
                        WHEN r.hs_heading = :heading AND r.hs_heading IS NOT NULL THEN 2
                        ELSE 3
                    END,
                    r.priority DESC
                LIMIT 5
            """),
            {
                "code": agreement_code.lower(),
                "heading": heading,
                "chapter": chapter,
                "subheading": subheading,
            },
        ).fetchall()

        if not rows:
            return None

        results = []
        for r in rows:
            results.append({
                "rule_type": r[0],
                "rule_text": r[1],
                "value_threshold": float(r[2]) if r[2] is not None else None,
                "rvc_method": r[3],
                "ts_heading_level": r[4],
                "ts_exceptions": r[5] or [],
                "secondary_rule_type": r[6],
                "secondary_value_threshold": float(r[7]) if r[7] is not None else None,
                "secondary_rvc_method": r[8],
                "source_reference": r[9],
            })
        return results

    except Exception:
        return None
    finally:
        conn.close()


# ─── Public tool functions ─────────────────────────────────────────────────────

def search_tariff_schedule(description: str, max_results: int = 5) -> list[dict]:
    """
    Search the HS tariff schedule for codes matching a product description.
    Queries DB (pg_trgm similarity) in production; falls back to keyword match in dev.
    Returns list of {hs_code, description, chapter, relevance_score}.
    """
    # Try DB path
    db_result = _db_search_hs(description, max_results)
    if db_result is not None:
        return db_result

    # Fallback: keyword match on bootstrap schedule
    desc_lower = description.lower()
    keywords = [w for w in desc_lower.split() if len(w) > 3]
    scored: list[tuple[int, str, dict]] = []
    for code, info in _BOOTSTRAP_HS.items():
        info_lower = info["description"].lower()
        score = sum(1 for kw in keywords if kw in info_lower)
        if score > 0:
            scored.append((score, code, info))
    scored.sort(key=lambda x: -x[0])
    return [
        {"hs_code": code, "description": info["description"],
         "chapter": info["chapter"], "relevance_score": score}
        for score, code, info in scored[:max_results]
    ]


def validate_hs_code(hs_code: str, country: str = "CA") -> dict:
    """
    Validate an HS code and retrieve its official description and chapter.
    Returns {valid, hs_code, description, chapter, notes}.
    """
    cleaned = re.sub(r"[.\s]", "", hs_code)
    if not re.match(r"^\d{4,10}$", cleaned):
        return {"valid": False, "hs_code": hs_code, "notes": "HS code must be 4–10 digits"}

    heading = cleaned[:4]

    # Try DB
    conn = _get_sync_conn()
    if conn:
        try:
            from sqlalchemy import text
            row = conn.execute(
                text("SELECT heading, chapter, description FROM hs_codes WHERE heading = :h AND is_heading = true LIMIT 1"),
                {"h": heading},
            ).fetchone()
            if row:
                return {
                    "valid": True, "hs_code": cleaned,
                    "description": row[2], "chapter": row[1],
                    "notes": "Validated against HS 2022 schedule",
                }
        except Exception:
            pass
        finally:
            conn.close()

    # Bootstrap fallback
    if heading in _BOOTSTRAP_HS:
        info = _BOOTSTRAP_HS[heading]
        return {
            "valid": True, "hs_code": cleaned,
            "description": info["description"], "chapter": info["chapter"],
            "notes": "Validated against bootstrap schedule",
        }

    return {
        "valid": True,
        "hs_code": cleaned,
        "description": "Description not available in local schedule — verify against full CAN tariff",
        "chapter": cleaned[:2],
        "notes": "Not found in local schedule; likely valid — verify at cbsa-asfc.gc.ca",
    }


def get_applicable_agreements(origin_country: str, destination_country: str) -> list[dict]:
    """
    Return trade agreements applicable to the origin → destination country pair.
    Queries DB in production; falls back to precomputed bootstrap map.
    """
    # Try DB
    db_result = _db_get_applicable_agreements(origin_country, destination_country)
    if db_result is not None:
        return db_result

    # Fallback: bootstrap FTA map
    global _BOOTSTRAP_FTA_MAP
    if not _BOOTSTRAP_FTA_MAP:
        _BOOTSTRAP_FTA_MAP = _build_bootstrap_fta_map()

    key = (origin_country.upper(), destination_country.upper())
    return _BOOTSTRAP_FTA_MAP.get(key, [])


def get_roo_rules(hs_code: str, agreement_code: str) -> list[dict]:
    """
    Fetch Rules of Origin for an HS code under a given agreement.
    Uses 3-level lookup: subheading → heading → chapter default.
    Queries DB in production; falls back to seed bootstrap rules in dev.
    """
    # Try DB
    db_result = _db_get_roo_rules(hs_code, agreement_code)
    if db_result is not None:
        return db_result

    # Fallback: bootstrap rules from seed data
    rules_index = _get_bootstrap_rules()
    if not rules_index:
        return []

    ag_rules = rules_index.get(agreement_code.lower(), {})
    if not ag_rules:
        return []

    cleaned = re.sub(r"[.\s]", "", hs_code)
    heading = cleaned[:4]
    chapter = cleaned[:2]

    # Priority: exact heading > chapter default
    if heading in ag_rules:
        return ag_rules[heading]
    if chapter in ag_rules:
        return ag_rules[chapter]

    return []


def run_roo_engine(
    hs_code: str,
    origin_country: str,
    destination_country: str,
    transaction_value_usd: float,
    bom_items: list[dict],
    agreement_codes: list[str] | None = None,
    net_cost_usd: float | None = None,
    product_description: str = "",
    wholly_obtained_category: str | None = None,
) -> dict:
    """
    Execute the deterministic RoO engine for a product shipment.

    Runs RVC, Tariff Shift, and Wholly Obtained checks against all applicable
    agreements and returns structured determination results with calibrated
    confidence scores.

    Args:
        hs_code: 4–6 digit HS code for the finished good
        origin_country: ISO-3166 alpha-2 production country
        destination_country: ISO-3166 alpha-2 destination country
        transaction_value_usd: ex-works / FOB price in USD
        bom_items: list of BOM components with {description, hs_code, origin_country, unit_cost, quantity, is_originating}
        agreement_codes: specific FTAs to evaluate; None = auto-detect from country pair
        net_cost_usd: net cost (required for Net Cost RVC method)
        product_description: plain text description
        wholly_obtained_category: "mineral" | "plant" | "fish" | etc.

    Returns:
        {agreements_evaluated, determinations, best_agreement, best_saving_usd,
         needs_human_review, review_reasons, confidence_summary}
    """
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "roo-engine"))

    try:
        from engine import RooEngine
        from models import BOMLine, ProductInfo, RooRule, RuleType

        # Resolve agreements
        if agreement_codes:
            agreements = [{"code": c} for c in agreement_codes]
        else:
            agreements = get_applicable_agreements(origin_country, destination_country)

        if not agreements:
            return {
                "agreements_evaluated": [],
                "determinations": [],
                "best_agreement": None,
                "best_saving_usd": None,
                "needs_human_review": True,
                "review_reasons": [f"No FTA found for {origin_country} → {destination_country}"],
                "error": None,
            }

        # Build RooRule lists per agreement
        rules_by_agreement: dict[str, list] = {}
        for ag in agreements:
            code = ag["code"]
            raw = get_roo_rules(hs_code, code)
            if raw:
                rules_list = []
                for r in raw:
                    try:
                        rule = RooRule(
                            agreement_code=code,
                            hs_chapter=None,
                            hs_heading=None,
                            hs_subheading=None,
                            rule_type=RuleType(r["rule_type"]),
                            rule_text=r.get("rule_text", ""),
                            value_threshold=r.get("value_threshold"),
                            rvc_method=r.get("rvc_method"),
                            ts_heading_level=r.get("ts_heading_level"),
                            ts_exceptions=r.get("ts_exceptions") or [],
                        )
                        rules_list.append(rule)
                    except ValueError:
                        continue
                if rules_list:
                    rules_by_agreement[code] = rules_list

        if not rules_by_agreement:
            return {
                "agreements_evaluated": [ag["code"] for ag in agreements],
                "determinations": [],
                "best_agreement": None,
                "best_saving_usd": None,
                "needs_human_review": True,
                "review_reasons": [f"No RoO rules found for HS {hs_code}"],
                "error": None,
            }

        # Build product model
        bom_lines = []
        for b in bom_items:
            bom_lines.append(BOMLine(
                description=b.get("description", ""),
                hs_code=b.get("hs_code"),
                origin_country=b.get("origin_country", "XX"),
                quantity=float(b.get("quantity", 1)),
                unit_cost=float(b.get("unit_cost", 0)),
                currency=b.get("currency", "USD"),
                unit_cost_usd=b.get("unit_cost_usd"),
                is_originating=b.get("is_originating"),
            ))

        product = ProductInfo(
            hs_code=hs_code,
            description=product_description,
            transaction_value_usd=transaction_value_usd,
            net_cost_usd=net_cost_usd,
            bom=bom_lines,
            production_country=origin_country,
            wholly_obtained_category=wholly_obtained_category,
        )

        engine = RooEngine()
        output = engine.evaluate(product, rules_by_agreement)

        return {
            "agreements_evaluated": output.agreements_evaluated,
            "determinations": [d.model_dump() for d in output.determinations],
            "best_agreement": output.best_agreement,
            "best_saving_usd": output.best_saving_usd,
            "needs_human_review": output.needs_human_review,
            "review_reasons": output.review_reasons,
            "error": None,
        }

    except Exception as exc:
        return {
            "agreements_evaluated": agreement_codes or [],
            "determinations": [],
            "best_agreement": None,
            "best_saving_usd": None,
            "needs_human_review": True,
            "review_reasons": [f"Engine error: {exc}"],
            "error": str(exc),
        }


def get_tariff_rates(hs_code: str, importing_country: str, agreement_code: str | None = None) -> dict:
    """
    Look up MFN and preferential tariff rates for an HS heading.

    Queries the tariff_rates table in production; returns placeholder structure
    in dev (the rates data pipeline is a separate feed).

    Args:
        hs_code: 4-digit HS heading
        importing_country: ISO-3166 alpha-2 country applying the tariff
        agreement_code: FTA code for preferential rate lookup (optional)

    Returns:
        {hs_heading, importing_country, mfn_rate, preferential_rate, agreement_code, source}
    """
    cleaned = re.sub(r"[.\s]", "", hs_code)[:4]

    conn = _get_sync_conn()
    if conn:
        try:
            from sqlalchemy import text
            row = conn.execute(
                text("""
                    SELECT hs_heading, importing_country, agreement_code,
                           rate_pct, rate_description, source
                    FROM tariff_rates
                    WHERE hs_heading = :h
                      AND importing_country = :country
                      AND (:code IS NULL OR agreement_code = :code)
                    ORDER BY CASE WHEN agreement_code IS NULL THEN 1 ELSE 0 END, rate_pct ASC
                    LIMIT 5
                """),
                {"h": cleaned, "country": importing_country.upper(), "code": agreement_code},
            ).fetchall()

            if row:
                mfn = next((r for r in row if r[2] is None), None)
                pref = next((r for r in row if r[2] == agreement_code), None) if agreement_code else None
                return {
                    "hs_heading": cleaned,
                    "importing_country": importing_country.upper(),
                    "mfn_rate": f"{mfn[3]:.1f}%" if mfn else "unknown",
                    "preferential_rate": f"{pref[3]:.1f}%" if pref else ("0%" if agreement_code else None),
                    "agreement_code": agreement_code,
                    "source": "tariff_rates table",
                }
        except Exception:
            pass
        finally:
            conn.close()

    # No rates DB yet — return structural placeholder so Claude can reason
    return {
        "hs_heading": cleaned,
        "importing_country": importing_country.upper(),
        "mfn_rate": "unavailable — tariff rates feed not yet loaded",
        "preferential_rate": "0% if agreement qualifies" if agreement_code else None,
        "agreement_code": agreement_code,
        "source": "placeholder — run tariff rates loader to populate",
    }


# ─── Claude tool schemas ──────────────────────────────────────────────────────

CLAUDE_TOOLS = [
    {
        "name": "search_tariff_schedule",
        "description": "Search the Harmonised System (HS) tariff schedule for codes matching a product description. Returns candidate HS codes ranked by relevance. Use this first when classifying an unknown product.",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Product description to search for",
                },
                "max_results": {"type": "integer", "default": 5},
            },
            "required": ["description"],
        },
    },
    {
        "name": "validate_hs_code",
        "description": "Validate an HS code and retrieve its official description and chapter from the tariff schedule.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hs_code": {
                    "type": "string",
                    "description": "The HS code to validate (4–10 digits, dots optional)",
                },
                "country": {"type": "string", "default": "CA"},
            },
            "required": ["hs_code"],
        },
    },
    {
        "name": "get_applicable_agreements",
        "description": "Get the list of free trade agreements applicable to an origin/destination country pair. Returns all active FTAs where both countries are parties.",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin_country": {
                    "type": "string",
                    "description": "ISO-3166 alpha-2 origin country code (e.g. CA, US, NG)",
                },
                "destination_country": {
                    "type": "string",
                    "description": "ISO-3166 alpha-2 destination country code",
                },
            },
            "required": ["origin_country", "destination_country"],
        },
    },
    {
        "name": "get_roo_rules",
        "description": "Fetch the applicable Rules of Origin for a specific HS code under a given trade agreement. Returns the most specific rule (subheading > heading > chapter default).",
        "input_schema": {
            "type": "object",
            "properties": {
                "hs_code": {
                    "type": "string",
                    "description": "HS code (4 or 6 digit). Examples: 8703, 870323, 6101",
                },
                "agreement_code": {
                    "type": "string",
                    "description": "FTA code. Options: cusma, ceta, cptpp, afcfta, ckfta, ccofta, cpafta",
                },
            },
            "required": ["hs_code", "agreement_code"],
        },
    },
    {
        "name": "run_roo_engine",
        "description": (
            "Execute the deterministic Rules of Origin compliance engine. "
            "Runs RVC (Build-Down, Build-Up, Net Cost), Tariff Shift, and Wholly Obtained "
            "checks against one or more trade agreements. Returns pass/fail per agreement "
            "with calibrated confidence scores and full calculation detail. "
            "Call this after you have retrieved the applicable agreements and rules."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "hs_code": {
                    "type": "string",
                    "description": "4–6 digit HS code of the finished good",
                },
                "origin_country": {
                    "type": "string",
                    "description": "ISO-3166 alpha-2 production country (e.g. CA, NG, MX)",
                },
                "destination_country": {
                    "type": "string",
                    "description": "ISO-3166 alpha-2 destination country",
                },
                "transaction_value_usd": {
                    "type": "number",
                    "description": "Ex-works or FOB price in USD",
                },
                "bom_items": {
                    "type": "array",
                    "description": "Bill of Materials components",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "hs_code": {"type": "string"},
                            "origin_country": {"type": "string"},
                            "unit_cost": {"type": "number"},
                            "quantity": {"type": "number"},
                            "is_originating": {"type": "boolean"},
                        },
                        "required": ["description", "origin_country", "unit_cost"],
                    },
                },
                "agreement_codes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "FTA codes to evaluate. Empty/null = auto-detect from country pair.",
                },
                "net_cost_usd": {
                    "type": "number",
                    "description": "Net cost in USD (required for Net Cost RVC method)",
                },
                "product_description": {"type": "string"},
                "wholly_obtained_category": {
                    "type": "string",
                    "description": "Category if product may qualify as wholly obtained: mineral, plant, fish, livestock, etc.",
                },
            },
            "required": ["hs_code", "origin_country", "destination_country", "transaction_value_usd", "bom_items"],
        },
    },
    {
        "name": "get_tariff_rates",
        "description": "Look up MFN (Most-Favoured-Nation) and preferential tariff rates for an HS heading in an importing country. Use to calculate potential savings from preferential origin.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hs_code": {
                    "type": "string",
                    "description": "4-digit HS heading",
                },
                "importing_country": {
                    "type": "string",
                    "description": "ISO-3166 alpha-2 importing country",
                },
                "agreement_code": {
                    "type": "string",
                    "description": "FTA code for preferential rate lookup (optional)",
                },
            },
            "required": ["hs_code", "importing_country"],
        },
    },
]


def dispatch_tool(name: str, inputs: dict) -> Any:
    """Dispatch a tool call by name."""
    dispatch: dict[str, Any] = {
        "search_tariff_schedule": search_tariff_schedule,
        "validate_hs_code": validate_hs_code,
        "get_applicable_agreements": get_applicable_agreements,
        "get_roo_rules": get_roo_rules,
        "run_roo_engine": run_roo_engine,
        "get_tariff_rates": get_tariff_rates,
    }
    if name not in dispatch:
        raise ValueError(f"Unknown tool: {name}")
    return dispatch[name](**inputs)

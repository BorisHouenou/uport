"""
RoO Database Loader
Populates trade_agreements, roo_rules, and hs_codes tables from seed data.

Usage:
    DATABASE_URL=postgresql://... python loader.py
    DATABASE_URL=postgresql://... python loader.py --fta cusma,ceta   # selective
    DATABASE_URL=postgresql://... python loader.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import sys
import uuid
from datetime import date

import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# Seed modules
from seed.agreements import AGREEMENTS
from seed.hs_schedule import CHAPTERS, HEADINGS
from seed.cusma_psrs import CUSMA_RULES
from seed.ceta_psrs import CETA_RULES
from seed.cptpp_psrs import CPTPP_RULES
from seed.afcfta_psrs import AFCFTA_RULES

PSR_MAP = {
    "cusma":  CUSMA_RULES,
    "ceta":   CETA_RULES,
    "cptpp":  CPTPP_RULES,
    "afcfta": AFCFTA_RULES,
}

# Rules for other FTAs that share CETA/CPTPP-style rules
ALIAS_MAP = {
    "cufta":  "ceta",
    "ckfta":  "cptpp",
}


def get_engine(database_url: str | None = None):
    url = database_url or os.getenv("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL not set")
    # Convert asyncpg URL to sync
    url = url.replace("+asyncpg", "").replace("postgresql://", "postgresql://")
    return create_engine(url, echo=False)


def load_hs_schedule(session: Session, dry_run: bool = False) -> int:
    """Upsert chapters and headings into hs_codes table."""
    count = 0

    # Chapters
    for ch in CHAPTERS:
        row = {
            "id": str(uuid.uuid4()),
            "chapter": ch["chapter"],
            "heading": None,
            "subheading": None,
            "description": ch["description"],
            "section": ch.get("section"),
            "is_heading": False,
            "is_subheading": False,
        }
        if not dry_run:
            session.execute(
                text("""
                    INSERT INTO hs_codes (id, chapter, heading, subheading, description, section, is_heading, is_subheading)
                    VALUES (:id, :chapter, :heading, :subheading, :description, :section, :is_heading, :is_subheading)
                    ON CONFLICT DO NOTHING
                """),
                row,
            )
        count += 1

    # Headings
    for (heading, chapter, description) in HEADINGS:
        row = {
            "id": str(uuid.uuid4()),
            "chapter": chapter,
            "heading": heading,
            "subheading": None,
            "description": description,
            "section": None,
            "is_heading": True,
            "is_subheading": False,
        }
        if not dry_run:
            session.execute(
                text("""
                    INSERT INTO hs_codes (id, chapter, heading, subheading, description, section, is_heading, is_subheading)
                    VALUES (:id, :chapter, :heading, :subheading, :description, :section, :is_heading, :is_subheading)
                    ON CONFLICT DO NOTHING
                """),
                row,
            )
        count += 1

    print(f"  HS schedule: {count} rows ({'dry-run' if dry_run else 'loaded'})")
    return count


def load_agreements(session: Session, dry_run: bool = False) -> dict[str, str]:
    """Upsert trade agreements. Returns code → id mapping."""
    code_to_id: dict[str, str] = {}
    for ag in AGREEMENTS:
        ag_id = str(uuid.uuid4())

        # Check if already exists
        result = session.execute(
            text("SELECT id FROM trade_agreements WHERE code = :code"),
            {"code": ag["code"]},
        ).fetchone()

        if result:
            ag_id = str(result[0])
        elif not dry_run:
            session.execute(
                text("""
                    INSERT INTO trade_agreements (id, code, name, parties, effective_date, is_active, description, source_url)
                    VALUES (:id, :code, :name, :parties, :effective_date, true, :description, :source_url)
                    ON CONFLICT (code) DO UPDATE SET
                        name = EXCLUDED.name,
                        parties = EXCLUDED.parties,
                        description = EXCLUDED.description,
                        source_url = EXCLUDED.source_url
                """),
                {
                    "id": ag_id,
                    "code": ag["code"],
                    "name": ag["name"],
                    "parties": ag["parties"],
                    "effective_date": date.fromisoformat(ag["effective_date"]),
                    "description": ag.get("description"),
                    "source_url": ag.get("source_url"),
                },
            )

        code_to_id[ag["code"]] = ag_id

    print(f"  Agreements: {len(code_to_id)} loaded")
    return code_to_id


def load_psr_rules(
    session: Session,
    agreement_code: str,
    agreement_id: str,
    rules: list[tuple],
    dry_run: bool = False,
) -> int:
    """Upsert PSR rules for one agreement. Returns number of rows inserted."""
    if not dry_run:
        # Delete existing rules for this agreement so we can reload cleanly
        session.execute(
            text("DELETE FROM roo_rules WHERE agreement_id = :ag_id"),
            {"ag_id": agreement_id},
        )

    count = 0
    for rule in rules:
        (hs_code, rule_type, rule_text, threshold, rvc_method, ts_level,
         sec_type, sec_threshold, sec_rvc, source_ref, is_default) = rule

        # Determine hs_chapter, hs_heading, hs_subheading from hs_code length
        hs_chapter = hs_heading = hs_subheading = None
        code_len = len(hs_code)
        if code_len == 2:
            hs_chapter = hs_code
        elif code_len == 4:
            hs_chapter = hs_code[:2]
            hs_heading = hs_code
        elif code_len >= 6:
            hs_chapter = hs_code[:2]
            hs_heading = hs_code[:4]
            hs_subheading = hs_code[:6]

        row = {
            "id": str(uuid.uuid4()),
            "agreement_id": agreement_id,
            "hs_chapter": hs_chapter,
            "hs_heading": hs_heading,
            "hs_subheading": hs_subheading,
            "rule_type": rule_type,
            "rule_text": rule_text,
            "value_threshold": threshold,
            "rvc_method": rvc_method,
            "ts_heading_level": ts_level,
            "secondary_rule_type": sec_type,
            "secondary_value_threshold": sec_threshold,
            "secondary_rvc_method": sec_rvc,
            "source_reference": source_ref,
            "is_default": is_default,
            "priority": 10 if not is_default else 0,
        }

        if not dry_run:
            session.execute(
                text("""
                    INSERT INTO roo_rules (
                        id, agreement_id, hs_chapter, hs_heading, hs_subheading,
                        rule_type, rule_text, value_threshold, rvc_method,
                        ts_heading_level, secondary_rule_type, secondary_value_threshold,
                        secondary_rvc_method, source_reference, is_default, priority
                    ) VALUES (
                        :id, :agreement_id, :hs_chapter, :hs_heading, :hs_subheading,
                        :rule_type, :rule_text, :value_threshold, :rvc_method,
                        :ts_heading_level, :secondary_rule_type, :secondary_value_threshold,
                        :secondary_rvc_method, :source_reference, :is_default, :priority
                    )
                """),
                row,
            )
        count += 1

    return count


def run(
    database_url: str | None = None,
    fta_filter: list[str] | None = None,
    dry_run: bool = False,
):
    engine = get_engine(database_url)

    with Session(engine) as session:
        print("\n── HS Schedule ──────────────────────────────────────────")
        load_hs_schedule(session, dry_run=dry_run)
        if not dry_run:
            session.commit()

        print("\n── Trade Agreements ─────────────────────────────────────")
        code_to_id = load_agreements(session, dry_run=dry_run)
        if not dry_run:
            session.commit()

        print("\n── PSR Rules ────────────────────────────────────────────")
        total_rules = 0
        for code, rules in PSR_MAP.items():
            if fta_filter and code not in fta_filter:
                continue
            ag_id = code_to_id.get(code)
            if not ag_id:
                print(f"  [{code}] SKIP — agreement not found in DB")
                continue
            count = load_psr_rules(session, code, ag_id, rules, dry_run=dry_run)
            print(f"  [{code.upper()}] {count} rules ({'dry-run' if dry_run else 'loaded'})")
            total_rules += count

        # Alias FTAs inherit rules from their base
        for alias_code, base_code in ALIAS_MAP.items():
            if fta_filter and alias_code not in fta_filter:
                continue
            if base_code not in PSR_MAP:
                continue
            ag_id = code_to_id.get(alias_code)
            if not ag_id:
                continue
            base_rules = PSR_MAP[base_code]
            count = load_psr_rules(session, alias_code, ag_id, base_rules, dry_run=dry_run)
            print(f"  [{alias_code.upper()}] {count} rules (inherited from {base_code.upper()})")
            total_rules += count

        if not dry_run:
            session.commit()

        print(f"\n✓ Total: {total_rules} PSR rules loaded across {len(PSR_MAP)} FTAs")

        if dry_run:
            print("  (dry-run — no changes committed)")


def main():
    parser = argparse.ArgumentParser(description="Load RoO rules database")
    parser.add_argument("--fta", type=str, help="Comma-separated FTA codes to load (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be loaded without committing")
    args = parser.parse_args()

    fta_filter = [c.strip().lower() for c in args.fta.split(",")] if args.fta else None
    run(fta_filter=fta_filter, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

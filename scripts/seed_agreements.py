"""
Seed script: populate trade_agreements and roo_rules tables.

Sourced from official FTA texts:
- CUSMA/USMCA Annex 4-B (Product-Specific Rules)
- CETA Annex II (Product-Specific Rules of Origin)
- CPTPP Annex 3-D (Product-Specific Rules)

Run: python scripts/seed_agreements.py
"""
import os
import sys
import uuid
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "api"))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from core.config import get_settings
from models.agreement import RooRule, TradeAgreement

settings = get_settings()
engine = create_engine(settings.database_url_sync)

# ─── Agreement definitions ─────────────────────────────────────────────────────

AGREEMENTS = [
    {
        "code": "cusma",
        "name": "Canada–United States–Mexico Agreement (CUSMA/USMCA)",
        "parties": ["CA", "US", "MX"],
        "effective_date": date(2020, 7, 1),
        "description": "Successor to NAFTA. Governs trade in goods, services, and IP between Canada, the United States, and Mexico.",
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/cusma-aceum/index.aspx",
    },
    {
        "code": "ceta",
        "name": "Comprehensive Economic and Trade Agreement (CETA)",
        "parties": [
            "CA", "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES",
            "FI", "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
            "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK",
        ],
        "effective_date": date(2017, 9, 21),
        "description": "Canada–EU trade agreement. Provisionally applied since Sept 2017. Covers 98% of tariff lines.",
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/ceta-aecg/index.aspx",
    },
    {
        "code": "cptpp",
        "name": "Comprehensive and Progressive Agreement for Trans-Pacific Partnership (CPTPP)",
        "parties": ["CA", "JP", "AU", "NZ", "SG", "VN", "MX", "CL", "PE", "MY", "BN"],
        "effective_date": date(2018, 12, 30),
        "description": "11-country Pacific Rim trade agreement. Canada entered into force Dec 30, 2018.",
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/cptpp-ptpgp/index.aspx",
    },
    {
        "code": "ccfta",
        "name": "Canada–Chile Free Trade Agreement (CCFTA)",
        "parties": ["CA", "CL"],
        "effective_date": date(1997, 7, 5),
        "description": "Canada's first FTA in South America.",
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/chile-chili/index.aspx",
    },
    {
        "code": "ckfta",
        "name": "Canada–Korea Free Trade Agreement (CKFTA)",
        "parties": ["CA", "KR"],
        "effective_date": date(2015, 1, 1),
        "description": "Canada–South Korea FTA.",
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/korea-coree/index.aspx",
    },
]

# ─── RoO rules (representative sample from official schedules) ─────────────────

ROO_RULES = {
    "cusma": [
        # Chapter 01 — Live animals
        {"hs_chapter": "01", "rule_type": "wholly_obtained",  "rule_text": "A good of Chapter 1 is originating if it is wholly obtained or produced entirely in the territory of one or more of the Parties. (CUSMA Art. 4.5)"},
        # Chapter 02 — Meat
        {"hs_chapter": "02", "rule_type": "wholly_obtained",  "rule_text": "Wholly obtained — animals born and raised in the territory of one or more Parties."},
        # Chapter 08 — Fruits
        {"hs_chapter": "08", "rule_type": "wholly_obtained",  "rule_text": "Wholly obtained — grown and harvested in the territory of one or more Parties."},
        # Chapter 61 — Knitted apparel (triple transformation / yarn-forward)
        {"hs_chapter": "61", "rule_type": "tariff_shift", "rule_text": "CC — A change to Chapter 61 from any other chapter, except from headings 51.06 through 51.13, 52.04 through 52.12, 53.07 through 53.08 or 53.10 through 53.11, subheading 5508.20, headings 55.09 through 55.16 or 58.01 through 58.06. (CUSMA Annex 4-B)", "ts_heading_level": "chapter"},
        # Chapter 73 — Iron/steel articles
        {"hs_heading": "7318", "rule_type": "rvc_build_down", "rule_text": "A change to heading 73.18 from any other heading; or no change in tariff classification required, provided there is a RVC of not less than 40% under the Build-Down method or 30% under the Net Cost method.", "value_threshold": 40.0, "rvc_method": "build_down"},
        {"hs_heading": "7326", "rule_type": "rvc_build_down", "rule_text": "RVC not less than 40% (Build-Down) or 30% (Net Cost). (CUSMA Annex 4-B)", "value_threshold": 40.0, "rvc_method": "build_down"},
        # Chapter 84 — Machinery
        {"hs_heading": "8471", "rule_type": "tariff_shift", "rule_text": "CTH — A change to heading 84.71 from any other heading.", "ts_heading_level": "heading"},
        {"hs_heading": "8479", "rule_type": "rvc_build_down", "rule_text": "A change to heading 84.79 from any other chapter; or a change to heading 84.79 from any other heading within Chapter 84, provided there is a RVC of not less than 50% (Build-Down) or 45% (Net Cost).", "value_threshold": 50.0, "rvc_method": "build_down"},
        # Chapter 85 — Electrical machinery
        {"hs_heading": "8517", "rule_type": "rvc_build_down", "rule_text": "A change to heading 85.17 from any other heading; or no required change in tariff classification, provided there is a RVC of not less than 40% (Build-Down) or 30% (Net Cost). (CUSMA Annex 4-B)", "value_threshold": 40.0, "rvc_method": "build_down"},
        {"hs_heading": "8528", "rule_type": "rvc_build_down", "rule_text": "RVC not less than 40% (Build-Down). (CUSMA Annex 4-B)", "value_threshold": 40.0, "rvc_method": "build_down"},
        {"hs_heading": "8544", "rule_type": "tariff_shift", "rule_text": "CTH — A change to heading 85.44 from any other heading.", "ts_heading_level": "heading"},
        # Chapter 87 — Vehicles
        {"hs_heading": "8703", "rule_type": "rvc_build_down", "rule_text": "No change in tariff classification required, provided there is a RVC of not less than 75% (Build-Down) or 65% (Net Cost). Core parts must also meet specific rules. (CUSMA Annex 4-B — Automotive)", "value_threshold": 75.0, "rvc_method": "build_down"},
        {"hs_heading": "8708", "rule_type": "rvc_build_down", "rule_text": "A change to heading 87.08 from any other heading; or RVC not less than 50% (Build-Down) or 45% (Net Cost). (CUSMA Annex 4-B)", "value_threshold": 50.0, "rvc_method": "build_down"},
    ],
    "ceta": [
        # CETA uses MaxNOM (Maximum Non-Originating Materials) — expressed as % of ex-works price
        # We model MaxNOM as Build-Down where threshold = 100 - MaxNOM
        {"hs_chapter": "01", "rule_type": "wholly_obtained",  "rule_text": "Wholly obtained (CETA Annex II, Chapter 1)"},
        {"hs_chapter": "02", "rule_type": "wholly_obtained",  "rule_text": "Wholly obtained (CETA Annex II, Chapter 2)"},
        {"hs_chapter": "61", "rule_type": "tariff_shift", "rule_text": "CC — Manufacture from yarn. (CETA Annex II, Section XI)", "ts_heading_level": "chapter"},
        {"hs_heading": "7318", "rule_type": "rvc_build_down", "rule_text": "MaxNOM 50% (EXW) — Non-originating materials must not exceed 50% of the ex-works price. Modelled as RVC ≥ 50% (Build-Down). (CETA Annex II)", "value_threshold": 50.0, "rvc_method": "build_down"},
        {"hs_heading": "8471", "rule_type": "tariff_shift", "rule_text": "CTH — A change from any other heading. MaxNOM 50% (EXW). (CETA Annex II)", "ts_heading_level": "heading"},
        {"hs_heading": "8517", "rule_type": "tariff_shift", "rule_text": "CTH — Change in tariff heading. (CETA Annex II, Chapter 85)", "ts_heading_level": "heading"},
        {"hs_heading": "8528", "rule_type": "rvc_build_down", "rule_text": "MaxNOM 50% (EXW). RVC ≥ 50% (Build-Down). (CETA Annex II)", "value_threshold": 50.0, "rvc_method": "build_down"},
        {"hs_heading": "8703", "rule_type": "rvc_build_down", "rule_text": "MaxNOM 45% (EXW) — Non-originating materials must not exceed 45% of the ex-works price. RVC ≥ 55% (Build-Down). (CETA Annex II, Chapter 87)", "value_threshold": 55.0, "rvc_method": "build_down"},
        {"hs_heading": "8708", "rule_type": "rvc_build_down", "rule_text": "MaxNOM 45% (EXW). RVC ≥ 55% (Build-Down). (CETA Annex II)", "value_threshold": 55.0, "rvc_method": "build_down"},
    ],
    "cptpp": [
        {"hs_chapter": "01", "rule_type": "wholly_obtained",  "rule_text": "Wholly obtained or produced entirely in the territory of a Party. (CPTPP Annex 3-D, Chapter 1)"},
        {"hs_chapter": "02", "rule_type": "wholly_obtained",  "rule_text": "Wholly obtained. (CPTPP Annex 3-D, Chapter 2)"},
        {"hs_chapter": "61", "rule_type": "tariff_shift", "rule_text": "CC — except from Chapter 50 through 63. (CPTPP Annex 3-D, Chapter 61)", "ts_heading_level": "chapter"},
        {"hs_heading": "7318", "rule_type": "rvc_build_down", "rule_text": "CTH; or RVC not less than 40% (Build-Down) or 30% (Net Cost). (CPTPP Annex 3-D)", "value_threshold": 40.0, "rvc_method": "build_down"},
        {"hs_heading": "8471", "rule_type": "tariff_shift", "rule_text": "CTH from any other heading. (CPTPP Annex 3-D)", "ts_heading_level": "heading"},
        {"hs_heading": "8517", "rule_type": "rvc_build_down", "rule_text": "CTH; or RVC not less than 40% (Build-Down). (CPTPP Annex 3-D, Chapter 85)", "value_threshold": 40.0, "rvc_method": "build_down"},
        {"hs_heading": "8703", "rule_type": "rvc_build_down", "rule_text": "RVC not less than 40% (Build-Down) or 30% (Net Cost). (CPTPP Annex 3-D, Chapter 87)", "value_threshold": 40.0, "rvc_method": "build_down"},
        {"hs_heading": "8708", "rule_type": "rvc_build_down", "rule_text": "CTH; or RVC not less than 40% (Build-Down) or 30% (Net Cost). (CPTPP Annex 3-D)", "value_threshold": 40.0, "rvc_method": "build_down"},
    ],
    "ckfta": [
        {"hs_chapter": "01", "rule_type": "wholly_obtained", "rule_text": "Wholly obtained. (CKFTA Annex 3-A)"},
        {"hs_heading": "8703", "rule_type": "rvc_build_down", "rule_text": "RVC not less than 55% (Build-Down) or 45% (Net Cost). (CKFTA Annex 3-A)", "value_threshold": 55.0, "rvc_method": "build_down"},
        {"hs_heading": "8517", "rule_type": "rvc_build_down", "rule_text": "CTH; or RVC not less than 45%. (CKFTA Annex 3-A)", "value_threshold": 45.0, "rvc_method": "build_down"},
    ],
}


def seed():
    with Session(engine) as session:
        for ag_data in AGREEMENTS:
            # Skip if already exists
            existing = session.execute(
                select(TradeAgreement).where(TradeAgreement.code == ag_data["code"])
            ).scalar_one_or_none()

            if existing:
                print(f"  [skip] {ag_data['code']} already exists")
                ag = existing
            else:
                ag = TradeAgreement(
                    id=uuid.uuid4(),
                    code=ag_data["code"],
                    name=ag_data["name"],
                    parties=ag_data["parties"],
                    effective_date=ag_data["effective_date"],
                    description=ag_data.get("description"),
                    source_url=ag_data.get("source_url"),
                )
                session.add(ag)
                session.flush()
                print(f"  [+] agreement: {ag_data['code']}")

            # Seed rules for this agreement
            rules_data = ROO_RULES.get(ag_data["code"], [])
            for rule_data in rules_data:
                rule = RooRule(
                    id=uuid.uuid4(),
                    agreement_id=ag.id,
                    hs_chapter=rule_data.get("hs_chapter"),
                    hs_heading=rule_data.get("hs_heading"),
                    hs_subheading=rule_data.get("hs_subheading"),
                    rule_type=rule_data["rule_type"],
                    rule_text=rule_data["rule_text"],
                    value_threshold=rule_data.get("value_threshold"),
                    tariff_shift_description=rule_data.get("ts_heading_level"),
                    notes=rule_data.get("notes"),
                )
                session.add(rule)

            if rules_data:
                print(f"  [+] {len(rules_data)} rules for {ag_data['code']}")

        session.commit()
        print("\nSeed complete.")


if __name__ == "__main__":
    print("Seeding trade agreements and RoO rules...")
    seed()

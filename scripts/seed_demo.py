#!/usr/bin/env python3
"""
Seed demo data for end-to-end testing on Railway.

Usage:
    DATABASE_URL=postgresql+asyncpg://... \
    DATABASE_URL_SYNC=postgresql+psycopg2://... \
    SEED_CLERK_USER_ID=user_xxxx \
    SEED_CLERK_ORG_ID=org_xxxx \
    python scripts/seed_demo.py

SEED_CLERK_USER_ID and SEED_CLERK_ORG_ID must match what Clerk puts in your JWT.
Find them at: https://dashboard.clerk.com → Users / Organizations.

If you have no Clerk org yet, omit SEED_CLERK_ORG_ID — a personal org will be created
and the API auth middleware will be patched to fall back to it.
"""
import asyncio
import os
import sys
import uuid
from datetime import date, timedelta

# Allow running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "api"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# ── Config ────────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("DATABASE_URL_ASYNC")
if not DATABASE_URL:
    # Try loading from apps/api/.env
    env_path = os.path.join(os.path.dirname(__file__), "..", "apps", "api", ".env")
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith("DATABASE_URL="):
                DATABASE_URL = line.split("=", 1)[1].strip().strip('"')
                break

if not DATABASE_URL:
    print("ERROR: Set DATABASE_URL env var (postgresql+asyncpg://user:pass@host/db)")
    sys.exit(1)

# Ensure asyncpg driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

CLERK_USER_ID = os.environ.get("SEED_CLERK_USER_ID", "user_demo_test_001")
CLERK_ORG_ID  = os.environ.get("SEED_CLERK_ORG_ID",  f"org_demo_{CLERK_USER_ID[-8:]}")

# Fixed UUIDs so the script is idempotent
ORG_ID      = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_ID     = uuid.UUID("00000000-0000-0000-0000-000000000002")
PRODUCT_1   = uuid.UUID("00000000-0000-0000-0000-000000000010")  # auto parts
PRODUCT_2   = uuid.UUID("00000000-0000-0000-0000-000000000011")  # electronics
PRODUCT_3   = uuid.UUID("00000000-0000-0000-0000-000000000012")  # machinery
SHIPMENT_1  = uuid.UUID("00000000-0000-0000-0000-000000000020")
SHIPMENT_2  = uuid.UUID("00000000-0000-0000-0000-000000000021")
SHIPMENT_3  = uuid.UUID("00000000-0000-0000-0000-000000000022")


async def seed(session: AsyncSession) -> None:
    # Bypass RLS for seed inserts
    await session.execute(text("SET LOCAL app.current_org_id = ''"))

    # ── Organization ──────────────────────────────────────────────────────────
    await session.execute(text("""
        INSERT INTO organizations
            (id, clerk_org_id, name, country, plan, subscription_tier,
             subscription_status, is_active, certificates_used, certificates_limit)
        VALUES
            (:id, :clerk_org_id, 'Acme Exports Inc.', 'CA', 'growth',
             'growth', 'active', true, 3, 100)
        ON CONFLICT (clerk_org_id) DO UPDATE
            SET name = EXCLUDED.name,
                subscription_tier = EXCLUDED.subscription_tier,
                subscription_status = EXCLUDED.subscription_status
    """), {"id": str(ORG_ID), "clerk_org_id": CLERK_ORG_ID})

    # ── User ──────────────────────────────────────────────────────────────────
    await session.execute(text("""
        INSERT INTO users
            (id, clerk_user_id, org_id, email, role, first_name, last_name, is_active)
        VALUES
            (:id, :clerk_user_id, :org_id,
             'demo@acmeexports.ca', 'org:admin', 'Demo', 'User', true)
        ON CONFLICT (clerk_user_id) DO UPDATE
            SET org_id = EXCLUDED.org_id,
                role   = EXCLUDED.role
    """), {"id": str(USER_ID), "clerk_user_id": CLERK_USER_ID, "org_id": str(ORG_ID)})

    # ── Products ──────────────────────────────────────────────────────────────
    products = [
        {
            "id": str(PRODUCT_1),
            "name": "Automotive Brake Assembly",
            "description": "Complete brake assembly for passenger vehicles, manufactured in Ontario, CA",
            "hs_code": "8708309900",
            "hs_description": "Brakes and servo-brakes and their parts — other",
            "hs_confidence": 0.94,
            "origin_country": "CA",
            "sku": "BRK-CA-001",
            "unit_cost_usd": 142.50,
        },
        {
            "id": str(PRODUCT_2),
            "name": "Industrial Control Module PCB",
            "description": "Printed circuit board for industrial automation, assembled in Canada with imported components",
            "hs_code": "8537109900",
            "hs_description": "Boards for electric control or distribution — other",
            "hs_confidence": 0.89,
            "origin_country": "CA",
            "sku": "PCB-IND-220",
            "unit_cost_usd": 87.00,
        },
        {
            "id": str(PRODUCT_3),
            "name": "CNC Precision Gear Set",
            "description": "Precision-machined gear set for industrial machinery, made in Quebec",
            "hs_code": "8483409900",
            "hs_description": "Gears and gearing — other",
            "hs_confidence": 0.91,
            "origin_country": "CA",
            "sku": "GEAR-QC-440",
            "unit_cost_usd": 215.00,
        },
    ]
    for p in products:
        await session.execute(text("""
            INSERT INTO products
                (id, org_id, name, description, hs_code, hs_description,
                 hs_confidence, origin_country, sku, unit_cost_usd)
            VALUES
                (:id, :org_id, :name, :description, :hs_code, :hs_description,
                 :hs_confidence, :origin_country, :sku, :unit_cost_usd)
            ON CONFLICT (id) DO UPDATE
                SET name = EXCLUDED.name, hs_code = EXCLUDED.hs_code
        """), {**p, "org_id": str(ORG_ID)})

    # ── BOM Items ─────────────────────────────────────────────────────────────
    bom_items = [
        # Brake assembly BOM
        {
            "product_id": str(PRODUCT_1), "description": "Steel brake disc, imported from US",
            "quantity": 2, "unit_cost": 18.50, "unit_cost_usd": 18.50,
            "origin_country": "US", "hs_code": "7325990000",
        },
        {
            "product_id": str(PRODUCT_1), "description": "Brake caliper casting, Canadian",
            "quantity": 1, "unit_cost": 42.00, "unit_cost_usd": 42.00,
            "origin_country": "CA", "hs_code": "8708309100",
        },
        {
            "product_id": str(PRODUCT_1), "description": "Friction pad set, Canadian",
            "quantity": 1, "unit_cost": 12.80, "unit_cost_usd": 12.80,
            "origin_country": "CA", "hs_code": "6813890000",
        },
        # PCB BOM
        {
            "product_id": str(PRODUCT_2), "description": "Microcontroller IC, imported from US",
            "quantity": 4, "unit_cost": 3.20, "unit_cost_usd": 3.20,
            "origin_country": "US", "hs_code": "8542319000",
        },
        {
            "product_id": str(PRODUCT_2), "description": "FR4 PCB substrate, Canadian",
            "quantity": 1, "unit_cost": 8.40, "unit_cost_usd": 8.40,
            "origin_country": "CA", "hs_code": "8534000000",
        },
        # Gear set BOM
        {
            "product_id": str(PRODUCT_3), "description": "Alloy steel billet, Canadian",
            "quantity": 1, "unit_cost": 65.00, "unit_cost_usd": 65.00,
            "origin_country": "CA", "hs_code": "7228309000",
        },
    ]
    for item in bom_items:
        await session.execute(text("""
            INSERT INTO bom_items
                (id, product_id, description, quantity, unit_cost,
                 currency, unit_cost_usd, origin_country, hs_code, classified_by)
            VALUES
                (gen_random_uuid(), :product_id, :description, :quantity, :unit_cost,
                 'USD', :unit_cost_usd, :origin_country, :hs_code, 'ai')
            ON CONFLICT DO NOTHING
        """), item)

    # ── Shipments ─────────────────────────────────────────────────────────────
    shipments = [
        {
            "id": str(SHIPMENT_1), "product_id": str(PRODUCT_1),
            "destination_country": "US", "origin_country": "CA",
            "incoterm": "DAP", "status": "pending",
            "shipment_value_usd": 14250.00, "reference_number": "SH-2026-001",
            "notes": "50-unit brake assembly shipment to Detroit auto manufacturer",
        },
        {
            "id": str(SHIPMENT_2), "product_id": str(PRODUCT_2),
            "destination_country": "DE", "origin_country": "CA",
            "incoterm": "CIF", "status": "pending",
            "shipment_value_usd": 8700.00, "reference_number": "SH-2026-002",
            "notes": "100-unit PCB shipment to German industrial client under CETA",
        },
        {
            "id": str(SHIPMENT_3), "product_id": str(PRODUCT_3),
            "destination_country": "JP", "origin_country": "CA",
            "incoterm": "FOB", "status": "pending",
            "shipment_value_usd": 21500.00, "reference_number": "SH-2026-003",
            "notes": "Gear set shipment to Japan under CPTPP",
        },
    ]
    for s in shipments:
        await session.execute(text("""
            INSERT INTO shipments
                (id, org_id, product_id, destination_country, origin_country,
                 incoterm, status, shipment_value_usd, reference_number, notes)
            VALUES
                (:id, :org_id, :product_id, :destination_country, :origin_country,
                 :incoterm, :status, :shipment_value_usd, :reference_number, :notes)
            ON CONFLICT (id) DO UPDATE
                SET reference_number = EXCLUDED.reference_number,
                    status = EXCLUDED.status
        """), {**s, "org_id": str(ORG_ID)})

    # ── Supplier Declarations ─────────────────────────────────────────────────
    suppliers = [
        {
            "product_id": str(PRODUCT_1),
            "supplier_name": "Great Lakes Steel Inc.",
            "supplier_country": "US", "origin_country": "US",
            "valid_from": date.today() - timedelta(days=90),
            "valid_until": date.today() + timedelta(days=275),
            "declaration_text": "We declare that the brake discs supplied are wholly obtained in the United States.",
        },
        {
            "product_id": str(PRODUCT_2),
            "supplier_name": "Texas Semiconductor Corp.",
            "supplier_country": "US", "origin_country": "US",
            "valid_from": date.today() - timedelta(days=60),
            "valid_until": date.today() + timedelta(days=305),
            "declaration_text": "We declare that the microcontroller ICs are manufactured in the United States.",
        },
    ]
    for sup in suppliers:
        await session.execute(text("""
            INSERT INTO supplier_declarations
                (id, org_id, product_id, supplier_name, supplier_country,
                 origin_country, valid_from, valid_until, declaration_text)
            VALUES
                (gen_random_uuid(), :org_id, :product_id, :supplier_name,
                 :supplier_country, :origin_country, :valid_from, :valid_until,
                 :declaration_text)
            ON CONFLICT DO NOTHING
        """), {**sup, "org_id": str(ORG_ID)})

    await session.commit()


async def main() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        await seed(session)

    await engine.dispose()

    print("\n✅  Demo data seeded successfully!\n")
    print(f"  Org ID      : {ORG_ID}")
    print(f"  Clerk Org ID: {CLERK_ORG_ID}")
    print(f"  Clerk User  : {CLERK_USER_ID}")
    print()
    print("  Shipments to test Origin Check:")
    print(f"    SH-2026-001  →  {SHIPMENT_1}  (CA→US, brake assembly, CUSMA)")
    print(f"    SH-2026-002  →  {SHIPMENT_2}  (CA→DE, PCB, CETA)")
    print(f"    SH-2026-003  →  {SHIPMENT_3}  (CA→JP, gears, CPTPP)")
    print()
    print("  Paste any of the UUIDs above into the Origin Check page.")
    print()


if __name__ == "__main__":
    asyncio.run(main())

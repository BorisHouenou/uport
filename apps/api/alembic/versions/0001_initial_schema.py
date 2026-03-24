"""Initial schema — all core tables

Revision ID: 0001
Revises:
Create Date: 2026-03-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable extensions (idempotent)
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # organizations
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("clerk_org_id", sa.String(128), nullable=False, unique=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("country", sa.String(2), nullable=False),
        sa.Column("plan", sa.String(32), nullable=False, server_default="starter"),
        sa.Column("stripe_customer_id", sa.String(128), unique=True),
        sa.Column("stripe_subscription_id", sa.String(128)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("certificates_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("certificates_limit", sa.Integer, nullable=False, server_default="10"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index("ix_organizations_clerk_org_id", "organizations", ["clerk_org_id"])

    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("clerk_user_id", sa.String(128), nullable=False, unique=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(256), nullable=False),
        sa.Column("role", sa.String(32), nullable=False, server_default="member"),
        sa.Column("first_name", sa.String(128)),
        sa.Column("last_name", sa.String(128)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_users_clerk_user_id", "users", ["clerk_user_id"])
    op.create_index("ix_users_org_id", "users", ["org_id"])
    op.create_index("ix_users_email", "users", ["email"])

    # products
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("hs_code", sa.String(10)),
        sa.Column("hs_description", sa.Text),
        sa.Column("hs_confidence", sa.Numeric(4, 3)),
        sa.Column("origin_country", sa.String(2)),
        sa.Column("sku", sa.String(128)),
        sa.Column("unit_cost_usd", sa.Numeric(14, 4)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_products_org_id", "products", ["org_id"])
    op.create_index("ix_products_hs_code", "products", ["hs_code"])

    # bom_items
    op.create_table(
        "bom_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("component_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="SET NULL")),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("quantity", sa.Numeric(14, 6), nullable=False),
        sa.Column("unit_cost", sa.Numeric(14, 4), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("unit_cost_usd", sa.Numeric(14, 4)),
        sa.Column("origin_country", sa.String(2), nullable=False),
        sa.Column("hs_code", sa.String(10)),
        sa.Column("hs_confidence", sa.Numeric(4, 3)),
        sa.Column("classified_by", sa.String(16), nullable=False, server_default="ai"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_bom_items_product_id", "bom_items", ["product_id"])

    # trade_agreements
    op.create_table(
        "trade_agreements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("parties", postgresql.ARRAY(sa.String(2)), nullable=False),
        sa.Column("effective_date", sa.Date, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("description", sa.Text),
        sa.Column("source_url", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_trade_agreements_code", "trade_agreements", ["code"])

    # roo_rules
    op.create_table(
        "roo_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("agreement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("trade_agreements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hs_chapter", sa.String(2)),
        sa.Column("hs_heading", sa.String(4)),
        sa.Column("hs_subheading", sa.String(6)),
        sa.Column("rule_type", sa.String(32), nullable=False),
        sa.Column("rule_text", sa.Text, nullable=False),
        sa.Column("value_threshold", sa.Float),
        sa.Column("tariff_shift_description", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_roo_rules_agreement_id", "roo_rules", ["agreement_id"])
    op.create_index("ix_roo_rules_hs_heading", "roo_rules", ["hs_heading"])

    # shipments
    op.create_table(
        "shipments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="SET NULL")),
        sa.Column("destination_country", sa.String(2), nullable=False),
        sa.Column("origin_country", sa.String(2), nullable=False),
        sa.Column("incoterm", sa.String(8)),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("shipment_value_usd", sa.Numeric(16, 2)),
        sa.Column("reference_number", sa.String(128)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_shipments_org_id", "shipments", ["org_id"])
    op.create_index("ix_shipments_status", "shipments", ["status"])

    # origin_determinations
    op.create_table(
        "origin_determinations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("shipment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agreement_code", sa.String(32), nullable=False),
        sa.Column("agreement_name", sa.String(256), nullable=False),
        sa.Column("rule_applied", sa.String(64), nullable=False),
        sa.Column("rule_text", sa.Text),
        sa.Column("result", sa.String(32), nullable=False),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=False),
        sa.Column("reasoning", sa.Text),
        sa.Column("raw_llm_response", postgresql.JSON),
        sa.Column("preferential_rate", sa.String(16)),
        sa.Column("mfn_rate", sa.String(16)),
        sa.Column("savings_per_unit", sa.Numeric(14, 4)),
        sa.Column("status", sa.String(32), nullable=False, server_default="completed"),
        sa.Column("reviewed_by", sa.String(256)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_origin_determinations_shipment_id", "origin_determinations", ["shipment_id"])
    op.create_index("ix_origin_determinations_agreement_code", "origin_determinations", ["agreement_code"])

    # certificates
    op.create_table(
        "certificates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("shipment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("determination_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("origin_determinations.id", ondelete="SET NULL")),
        sa.Column("cert_type", sa.String(32), nullable=False),
        sa.Column("pdf_url", sa.Text),
        sa.Column("s3_key", sa.Text),
        sa.Column("issued_at", sa.DateTime(timezone=True)),
        sa.Column("valid_until", sa.DateTime(timezone=True)),
        sa.Column("digital_signature", sa.Text),
        sa.Column("cert_number", sa.String(64), unique=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("exporter_ref", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_certificates_shipment_id", "certificates", ["shipment_id"])

    # supplier_declarations
    op.create_table(
        "supplier_declarations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("supplier_name", sa.String(512), nullable=False),
        sa.Column("supplier_country", sa.String(2), nullable=False),
        sa.Column("origin_country", sa.String(2), nullable=False),
        sa.Column("valid_from", sa.Date, nullable=False),
        sa.Column("valid_until", sa.Date, nullable=False),
        sa.Column("declaration_text", sa.Text),
        sa.Column("doc_url", sa.Text),
        sa.Column("s3_key", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_supplier_declarations_org_id", "supplier_declarations", ["org_id"])
    op.create_index("ix_supplier_declarations_product_id", "supplier_declarations", ["product_id"])

    # audit_events (immutable — no updated_at)
    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True)),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(128)),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("actor_id", sa.String(128)),
        sa.Column("actor_email", sa.String(256)),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("payload", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_events_org_id", "audit_events", ["org_id"])
    op.create_index("ix_audit_events_entity_type", "audit_events", ["entity_type"])
    op.create_index("ix_audit_events_created_at", "audit_events", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("supplier_declarations")
    op.drop_table("certificates")
    op.drop_table("origin_determinations")
    op.drop_table("shipments")
    op.drop_table("roo_rules")
    op.drop_table("trade_agreements")
    op.drop_table("bom_items")
    op.drop_table("products")
    op.drop_table("users")
    op.drop_table("organizations")

"""RoO database enhancements: hs_codes table + roo_rules new columns

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-30
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── hs_codes ──────────────────────────────────────────────────────────────
    op.create_table(
        "hs_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("chapter", sa.String(2), nullable=False),
        sa.Column("heading", sa.String(4)),
        sa.Column("subheading", sa.String(6)),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("section", sa.String(4)),       # Roman numeral e.g. "I", "XVI"
        sa.Column("section_title", sa.Text),
        sa.Column("chapter_title", sa.Text),
        sa.Column("is_heading", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_subheading", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_hs_codes_chapter", "hs_codes", ["chapter"])
    op.create_index("ix_hs_codes_heading", "hs_codes", ["heading"])
    op.create_index("ix_hs_codes_subheading", "hs_codes", ["subheading"])
    op.create_index("ix_hs_codes_description_trgm", "hs_codes", ["description"],
                    postgresql_using="gin",
                    postgresql_ops={"description": "gin_trgm_ops"})

    # ── tariff_rates ──────────────────────────────────────────────────────────
    op.create_table(
        "tariff_rates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("hs_heading", sa.String(6), nullable=False),
        sa.Column("importing_country", sa.String(2), nullable=False),
        sa.Column("agreement_code", sa.String(32)),          # NULL = MFN rate
        sa.Column("rate_pct", sa.Numeric(6, 2)),             # NULL = ad valorem unknown
        sa.Column("rate_description", sa.String(64)),        # e.g. "Free", "6.5%", "Specific"
        sa.Column("effective_date", sa.Date),
        sa.Column("source", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tariff_rates_hs_heading", "tariff_rates", ["hs_heading"])
    op.create_index("ix_tariff_rates_lookup", "tariff_rates",
                    ["hs_heading", "importing_country", "agreement_code"])

    # ── roo_rules new columns ─────────────────────────────────────────────────
    op.add_column("roo_rules", sa.Column("rvc_method", sa.String(16)))
    op.add_column("roo_rules", sa.Column("ts_heading_level", sa.String(16)))
    op.add_column("roo_rules", sa.Column("ts_exceptions", postgresql.JSONB))
    op.add_column("roo_rules", sa.Column("secondary_rule_type", sa.String(32)))
    op.add_column("roo_rules", sa.Column("secondary_value_threshold", sa.Float))
    op.add_column("roo_rules", sa.Column("secondary_rvc_method", sa.String(16)))
    op.add_column("roo_rules", sa.Column("hs_range_from", sa.String(4)))
    op.add_column("roo_rules", sa.Column("hs_range_to", sa.String(4)))
    op.add_column("roo_rules", sa.Column("priority", sa.Integer, server_default="0"))
    op.add_column("roo_rules", sa.Column("source_reference", sa.String(256)))
    op.add_column("roo_rules", sa.Column("is_default", sa.Boolean, server_default="false"))

    # Composite lookup index: (agreement_id, hs_heading) — used on every origin check
    op.create_index("ix_roo_rules_agreement_heading",
                    "roo_rules", ["agreement_id", "hs_heading"])
    op.create_index("ix_roo_rules_agreement_chapter",
                    "roo_rules", ["agreement_id", "hs_chapter"])
    op.create_index("ix_roo_rules_agreement_subheading",
                    "roo_rules", ["agreement_id", "hs_subheading"])


def downgrade() -> None:
    op.drop_index("ix_roo_rules_agreement_subheading", "roo_rules")
    op.drop_index("ix_roo_rules_agreement_chapter", "roo_rules")
    op.drop_index("ix_roo_rules_agreement_heading", "roo_rules")
    for col in ["rvc_method", "ts_heading_level", "ts_exceptions",
                "secondary_rule_type", "secondary_value_threshold",
                "secondary_rvc_method", "hs_range_from", "hs_range_to",
                "priority", "source_reference", "is_default"]:
        op.drop_column("roo_rules", col)
    op.drop_index("ix_tariff_rates_lookup", "tariff_rates")
    op.drop_index("ix_tariff_rates_hs_heading", "tariff_rates")
    op.drop_table("tariff_rates")
    op.drop_index("ix_hs_codes_description_trgm", "hs_codes")
    op.drop_index("ix_hs_codes_subheading", "hs_codes")
    op.drop_index("ix_hs_codes_heading", "hs_codes")
    op.drop_index("ix_hs_codes_chapter", "hs_codes")
    op.drop_table("hs_codes")

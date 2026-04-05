"""Add human_corrections table for fine-tuning data pipeline.

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "human_corrections",
        sa.Column("id",               postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id",           postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("determination_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("origin_determinations.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("original_hs_code",   sa.String(16)),
        sa.Column("corrected_hs_code",  sa.String(16)),
        sa.Column("original_result",    sa.String(32)),
        sa.Column("corrected_result",   sa.String(32)),
        sa.Column("original_rule",      sa.String(64)),
        sa.Column("corrected_rule",     sa.String(64)),
        sa.Column("agreement_code",     sa.String(32)),
        sa.Column("reviewer_id",        sa.String(128)),
        sa.Column("reviewer_notes",     sa.Text),
        sa.Column("product_description", sa.Text),
        sa.Column("exported_at",        sa.DateTime(timezone=True)),  # null = not yet exported
        sa.Column("created_at",         sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    # ix_human_corrections_org_id already created by index=True on org_id column
    # ix_human_corrections_determination_id already created by index=True on determination_id column
    op.create_index("ix_human_corrections_exported_at", "human_corrections", ["exported_at"])


def downgrade() -> None:
    op.drop_table("human_corrections")

"""Add webhook_endpoints table and supplier notified_expired flag.

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── webhook_endpoints ──────────────────────────────────────────────────────
    op.create_table(
        "webhook_endpoints",
        sa.Column("id",          postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id",      postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("url",         sa.Text,        nullable=False),
        sa.Column("secret",      sa.String(128), nullable=False),
        sa.Column("events",      postgresql.ARRAY(sa.String(64)), nullable=False, server_default="{}"),
        sa.Column("active",      sa.Boolean,     nullable=False, server_default="true"),
        sa.Column("description", sa.String(256)),
        sa.Column("created_at",  sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",  sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    # index already created by index=True on the org_id column above

    # ── supplier_declarations.notified_expired ─────────────────────────────────
    op.add_column(
        "supplier_declarations",
        sa.Column("notified_expired", sa.Boolean, nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("supplier_declarations", "notified_expired")
    op.drop_index("ix_webhook_endpoints_org_id", table_name="webhook_endpoints")
    op.drop_table("webhook_endpoints")

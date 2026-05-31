"""Add calibration_stats table for confidence model accuracy tracking.

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "calibration_stats",
        sa.Column("id",          sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("stats",       postgresql.JSONB, nullable=False),
    )
    op.create_index("ix_calibration_stats_computed_at", "calibration_stats", ["computed_at"])

    # Extend human_corrections with hs_code context fields for richer JSONL exports
    op.add_column("human_corrections", sa.Column("hs_chapter", sa.String(4)))
    op.add_column("human_corrections", sa.Column("origin_country", sa.String(8)))
    op.add_column("human_corrections", sa.Column("destination_country", sa.String(8)))
    op.add_column("human_corrections", sa.Column("rvc_pct", sa.Float))
    op.add_column("human_corrections", sa.Column("confidence_at_review", sa.Float))


def downgrade() -> None:
    op.drop_column("human_corrections", "confidence_at_review")
    op.drop_column("human_corrections", "rvc_pct")
    op.drop_column("human_corrections", "destination_country")
    op.drop_column("human_corrections", "origin_country")
    op.drop_column("human_corrections", "hs_chapter")
    op.drop_table("calibration_stats")

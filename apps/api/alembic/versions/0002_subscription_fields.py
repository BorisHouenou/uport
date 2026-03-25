"""Add subscription_tier, subscription_status to organizations; add chat_messages table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── organizations: subscription columns ───────────────────────────────────
    op.add_column(
        "organizations",
        sa.Column("subscription_tier", sa.String(32), nullable=False, server_default="starter"),
    )
    op.add_column(
        "organizations",
        sa.Column("subscription_status", sa.String(32), nullable=False, server_default="none"),
    )

    # ── chat_messages ─────────────────────────────────────────────────────────
    op.create_table(
        "chat_messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("user_id", sa.String(256), nullable=False, index=True),
        sa.Column("role", sa.String(16), nullable=False),       # user | assistant
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("citations", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_chat_messages_user_created", "chat_messages", ["user_id", "created_at"])

    # ── integration_tokens ────────────────────────────────────────────────────
    # Created dynamically by integration_service; ensure it exists in schema.
    op.execute("""
        CREATE TABLE IF NOT EXISTS integration_tokens (
            org_id   TEXT NOT NULL,
            provider TEXT NOT NULL,
            data     JSONB NOT NULL,
            PRIMARY KEY (org_id, provider)
        )
    """)

    # ── document_chunks (pgvector RAG store) ─────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id          SERIAL PRIMARY KEY,
            agreement   TEXT NOT NULL,
            source      TEXT NOT NULL,
            content     TEXT NOT NULL,
            embedding   vector(1536),
            created_at  TIMESTAMPTZ DEFAULT now()
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS document_chunks_emb_idx "
        "ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.drop_index("document_chunks_emb_idx", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_table("integration_tokens")
    op.drop_index("ix_chat_messages_user_created", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_column("organizations", "subscription_status")
    op.drop_column("organizations", "subscription_tier")

"""Widen hs_codes.section from VARCHAR(4) to VARCHAR(8)

Roman numeral section labels like 'XVIII' (5 chars) exceed the original
VARCHAR(4) limit. Widen to VARCHAR(8) to cover all 21 HS sections safely.

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("hs_codes", "section", type_=sa.String(8), existing_nullable=True)


def downgrade() -> None:
    op.alter_column("hs_codes", "section", type_=sa.String(4), existing_nullable=True)

"""Human correction model — fine-tuning data collection."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class HumanCorrection(Base):
    __tablename__ = "human_corrections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    determination_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("origin_determinations.id", ondelete="SET NULL"), nullable=True, index=True)
    original_hs_code: Mapped[str | None] = mapped_column(String(16))
    corrected_hs_code: Mapped[str | None] = mapped_column(String(16))
    original_result: Mapped[str | None] = mapped_column(String(32))
    corrected_result: Mapped[str | None] = mapped_column(String(32))
    original_rule: Mapped[str | None] = mapped_column(String(64))
    corrected_rule: Mapped[str | None] = mapped_column(String(64))
    agreement_code: Mapped[str | None] = mapped_column(String(32))
    reviewer_id: Mapped[str | None] = mapped_column(String(128))
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    product_description: Mapped[str | None] = mapped_column(Text)
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()", nullable=False)

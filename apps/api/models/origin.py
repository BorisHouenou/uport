import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.shipment import Shipment


class OriginDetermination(Base, TimestampMixin):
    __tablename__ = "origin_determinations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agreement_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    agreement_name: Mapped[str] = mapped_column(String(256), nullable=False)
    rule_applied: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_text: Mapped[str | None] = mapped_column(Text)
    result: Mapped[str] = mapped_column(String(32), nullable=False)  # pass/fail/insufficient_data
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text)
    raw_llm_response: Mapped[dict | None] = mapped_column(JSON)
    preferential_rate: Mapped[str | None] = mapped_column(String(16))
    mfn_rate: Mapped[str | None] = mapped_column(String(16))
    savings_per_unit: Mapped[float | None] = mapped_column(Numeric(14, 4))
    status: Mapped[str] = mapped_column(String(32), default="completed", nullable=False)
    reviewed_by: Mapped[str | None] = mapped_column(String(256))

    shipment: Mapped["Shipment"] = relationship("Shipment", back_populates="determinations")

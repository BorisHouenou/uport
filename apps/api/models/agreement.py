import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Float, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class TradeAgreement(Base, TimestampMixin):
    __tablename__ = "trade_agreements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    parties: Mapped[list[str]] = mapped_column(ARRAY(String(2)), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)

    rules: Mapped[list["RooRule"]] = relationship("RooRule", back_populates="agreement")


class RooRule(Base, TimestampMixin):
    __tablename__ = "roo_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agreement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    hs_chapter: Mapped[str | None] = mapped_column(String(2), index=True)
    hs_heading: Mapped[str | None] = mapped_column(String(4), index=True)
    hs_subheading: Mapped[str | None] = mapped_column(String(6), index=True)
    rule_type: Mapped[str] = mapped_column(String(32), nullable=False)
    rule_text: Mapped[str] = mapped_column(Text, nullable=False)
    value_threshold: Mapped[float | None] = mapped_column(Float)
    tariff_shift_description: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    agreement: Mapped["TradeAgreement"] = relationship("TradeAgreement", back_populates="rules")

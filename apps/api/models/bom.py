import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.product import Product


class BOMItem(Base, TimestampMixin):
    __tablename__ = "bom_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    component_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL")
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(14, 6), nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    unit_cost_usd: Mapped[float | None] = mapped_column(Numeric(14, 4))
    origin_country: Mapped[str] = mapped_column(String(2), nullable=False, comment="ISO-3166 alpha-2")
    hs_code: Mapped[str | None] = mapped_column(String(10))
    hs_confidence: Mapped[float | None] = mapped_column(Numeric(4, 3))
    classified_by: Mapped[str] = mapped_column(String(16), default="ai", nullable=False)

    product: Mapped["Product"] = relationship("Product", foreign_keys=[product_id], back_populates="bom_items")

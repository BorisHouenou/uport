import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.organization import Organization
    from models.bom import BOMItem


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    hs_code: Mapped[str | None] = mapped_column(String(10), index=True)
    hs_description: Mapped[str | None] = mapped_column(Text)
    hs_confidence: Mapped[float | None] = mapped_column(Numeric(4, 3))
    origin_country: Mapped[str | None] = mapped_column(String(2), comment="ISO-3166 alpha-2")
    sku: Mapped[str | None] = mapped_column(String(128))
    unit_cost_usd: Mapped[float | None] = mapped_column(Numeric(14, 4))

    organization: Mapped["Organization"] = relationship("Organization", back_populates="products")
    bom_items: Mapped[list["BOMItem"]] = relationship("BOMItem", back_populates="product", foreign_keys="BOMItem.product_id")

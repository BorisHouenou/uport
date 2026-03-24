import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.organization import Organization
    from models.origin import OriginDetermination
    from models.certificate import Certificate


class Shipment(Base, TimestampMixin):
    __tablename__ = "shipments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    destination_country: Mapped[str] = mapped_column(String(2), nullable=False, comment="ISO-3166 alpha-2")
    origin_country: Mapped[str] = mapped_column(String(2), nullable=False)
    incoterm: Mapped[str | None] = mapped_column(String(8))
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)
    shipment_value_usd: Mapped[float | None] = mapped_column(Numeric(16, 2))
    reference_number: Mapped[str | None] = mapped_column(String(128))
    notes: Mapped[str | None] = mapped_column(Text)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="shipments")
    determinations: Mapped[list["OriginDetermination"]] = relationship("OriginDetermination", back_populates="shipment")
    certificates: Mapped[list["Certificate"]] = relationship("Certificate", back_populates="shipment")

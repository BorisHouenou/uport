import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin

if TYPE_CHECKING:
    from models.user import User
    from models.product import Product
    from models.shipment import Shipment


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_org_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False, comment="ISO-3166 alpha-2")
    plan: Mapped[str] = mapped_column(String(32), default="starter", nullable=False)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(128), unique=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    certificates_used: Mapped[int] = mapped_column(default=0, nullable=False)
    certificates_limit: Mapped[int] = mapped_column(default=10, nullable=False)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="organization")
    products: Mapped[list["Product"]] = relationship("Product", back_populates="organization")
    shipments: Mapped[list["Shipment"]] = relationship("Shipment", back_populates="organization")

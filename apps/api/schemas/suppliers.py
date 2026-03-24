import uuid
from datetime import date

from pydantic import Field

from schemas.base import TimestampMixin, UportaiBase


class SupplierDeclarationCreate(UportaiBase):
    product_id: uuid.UUID
    supplier_name: str
    supplier_country: str = Field(description="ISO-3166 alpha-2")
    origin_country: str = Field(description="ISO-3166 alpha-2")
    valid_from: date
    valid_until: date
    declaration_text: str | None = None


class SupplierDeclarationResponse(TimestampMixin):
    id: uuid.UUID
    product_id: uuid.UUID
    supplier_name: str
    supplier_country: str
    origin_country: str
    valid_from: date
    valid_until: date
    doc_url: str | None = None
    is_expired: bool = False


class SupplierDeclarationList(UportaiBase):
    declarations: list[SupplierDeclarationResponse]
    total: int
    expiring_soon: int

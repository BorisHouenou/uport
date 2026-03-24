import uuid
from typing import Literal

from pydantic import Field

from schemas.base import TaskResponse, TimestampMixin, UportaiBase


class BOMItemBase(UportaiBase):
    description: str
    quantity: float
    unit_cost: float
    currency: str = "USD"
    origin_country: str = Field(description="ISO-3166 alpha-2")
    hs_code: str | None = None
    hs_confidence: float | None = None


class BOMItemCreate(BOMItemBase):
    pass


class BOMItem(BOMItemBase, TimestampMixin):
    id: uuid.UUID
    product_id: uuid.UUID
    total_cost: float
    classified_by: Literal["ai", "manual", "imported"] = "ai"


class BOMItemList(UportaiBase):
    product_id: uuid.UUID
    items: list[BOMItem]
    total_items: int
    total_cost_usd: float
    foreign_content_pct: float | None = None


class BOMUploadResponse(TaskResponse):
    product_id: uuid.UUID
    rows_detected: int | None = None

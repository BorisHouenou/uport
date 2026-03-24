import uuid
from datetime import datetime
from typing import Literal

from schemas.base import TaskResponse, TimestampMixin, UportaiBase

CertType = Literal["cusma", "eur1", "form_a", "generic"]


class CertificateCreate(UportaiBase):
    shipment_id: uuid.UUID
    determination_id: uuid.UUID
    cert_type: CertType = "cusma"
    exporter_ref: str | None = None


class CertificateResponse(TaskResponse):
    shipment_id: uuid.UUID
    cert_type: CertType
    certificate_id: uuid.UUID | None = None
    pdf_url: str | None = None
    issued_at: datetime | None = None
    valid_until: datetime | None = None


class CertificateSummary(TimestampMixin):
    id: uuid.UUID
    shipment_id: uuid.UUID
    cert_type: CertType
    pdf_url: str
    issued_at: datetime
    valid_until: datetime | None


class CertificateListResponse(UportaiBase):
    certificates: list[CertificateSummary]
    total: int
    page: int
    page_size: int

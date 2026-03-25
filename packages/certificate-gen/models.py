"""Certificate data models — shared between generator and API."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


CertType = Literal["cusma", "eur1", "form_a", "generic"]


class ExporterInfo(BaseModel):
    name: str
    address: str
    country: str
    tax_id: str | None = None
    contact_email: str | None = None


class ImporterInfo(BaseModel):
    name: str
    address: str
    country: str


class GoodLine(BaseModel):
    line_no: int
    description: str
    hs_code: str
    origin_country: str
    quantity: float
    unit: str = "units"
    unit_value_usd: float
    total_value_usd: float


class CertificateData(BaseModel):
    """All data needed to render any certificate type."""
    cert_type: CertType
    cert_number: str
    agreement_code: str
    agreement_name: str
    exporter: ExporterInfo
    importer: ImporterInfo
    goods: list[GoodLine]
    origin_criterion: str          # e.g. "B" (CUSMA), "CTH" (CETA)
    blanket_period_start: date | None = None
    blanket_period_end: date | None = None
    invoice_number: str | None = None
    invoice_date: date | None = None
    transport_mode: str | None = None
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    issued_by: str = ""
    rule_applied: str = ""
    rvc_pct: float | None = None
    exporter_declaration: str = (
        "I certify that the goods described in this document qualify as originating "
        "and the information contained in this document is true and accurate. "
        "I assume responsibility for proving such representations and agree to maintain "
        "and present upon request, or to provide access to, any records necessary to "
        "support this certification."
    )

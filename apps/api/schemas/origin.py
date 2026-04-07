import uuid
from typing import Literal

from pydantic import Field

from schemas.base import TaskResponse, TimestampMixin, UportaiBase

RuleType = Literal["tariff_shift", "rvc_build_down", "rvc_build_up", "rvc_net_cost", "wholly_obtained"]
DeterminationStatus = Literal["queued", "processing", "completed", "failed", "needs_review"]


class OriginDeterminationCreate(UportaiBase):
    shipment_id: uuid.UUID
    agreement_codes: list[str] = Field(
        default=["cusma"],
        description="FTA codes to evaluate, e.g. ['cusma', 'ceta', 'cptpp']",
    )


class AgreementResult(UportaiBase):
    agreement_code: str
    agreement_name: str
    rule_applied: RuleType
    rule_text: str
    result: Literal["pass", "fail", "insufficient_data"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    preferential_rate: str | None = None
    mfn_rate: str | None = None
    savings_per_unit: float | None = None


class OriginDeterminationResponse(TaskResponse):
    shipment_id: uuid.UUID
    results: list[AgreementResult] | None = None
    best_agreement: str | None = None
    total_savings_usd: float | None = None


class OriginQueryRequest(UportaiBase):
    pass


class OriginQueryResponse(UportaiBase):
    id: uuid.UUID
    shipment_id: uuid.UUID
    status: DeterminationStatus
    results: list[AgreementResult]
    best_agreement: str | None
    total_savings_usd: float | None
    reviewed_by: str | None = None

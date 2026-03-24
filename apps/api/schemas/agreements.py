import uuid
from datetime import date
from typing import Literal

from schemas.base import TaskResponse, UportaiBase

RuleType = Literal["tariff_shift", "rvc_build_down", "rvc_build_up", "rvc_net_cost", "wholly_obtained", "combined"]


class Agreement(UportaiBase):
    id: uuid.UUID
    code: str
    name: str
    parties: list[str]
    effective_date: date
    is_active: bool = True


class AgreementList(UportaiBase):
    agreements: list[Agreement]
    total: int


class RooRule(UportaiBase):
    id: uuid.UUID
    agreement_code: str
    hs_chapter: str | None
    hs_heading: str | None
    hs_subheading: str | None
    rule_type: RuleType
    rule_text: str
    value_threshold: float | None = None
    tariff_shift_description: str | None = None


class RooRuleList(UportaiBase):
    agreement_code: str
    rules: list[RooRule]
    total: int


class HSCodeClassification(TaskResponse):
    description: str
    hs_code: str | None = None
    hs_description: str | None = None
    confidence: float | None = None
    alternatives: list[dict] | None = None

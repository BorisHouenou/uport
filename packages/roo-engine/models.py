"""Pydantic models for the RoO calculation engine."""
from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class RuleType(str, Enum):
    TARIFF_SHIFT = "tariff_shift"
    RVC_BUILD_DOWN = "rvc_build_down"
    RVC_BUILD_UP = "rvc_build_up"
    RVC_NET_COST = "rvc_net_cost"
    WHOLLY_OBTAINED = "wholly_obtained"
    COMBINED = "combined"  # e.g. TS + RVC


class DeterminationResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INSUFFICIENT_DATA = "insufficient_data"


class BOMLine(BaseModel):
    """A single line item in a Bill of Materials."""
    description: str
    hs_code: str | None = None          # 6-digit preferred
    origin_country: str                  # ISO-3166 alpha-2
    quantity: float = 1.0
    unit_cost: float                     # in transaction currency
    currency: str = "USD"
    unit_cost_usd: float | None = None  # normalised
    is_originating: bool | None = None  # None = unknown


class ProductInfo(BaseModel):
    """The finished product being assessed."""
    hs_code: str                         # output HS code (6-digit)
    description: str
    transaction_value_usd: float         # ex-works / FOB price
    net_cost_usd: float | None = None
    bom: list[BOMLine] = Field(default_factory=list)
    wholly_obtained_category: str | None = None  # e.g. "mineral", "plant", "fish"
    production_country: str             # ISO-3166 alpha-2


class RooRule(BaseModel):
    """A single Rule of Origin from a trade agreement schedule."""
    agreement_code: str
    hs_chapter: str | None = None       # 2-digit
    hs_heading: str | None = None       # 4-digit
    hs_subheading: str | None = None    # 6-digit
    rule_type: RuleType
    rule_text: str
    # For RVC rules
    value_threshold: float | None = None   # e.g. 40.0 for 40% RVC
    rvc_method: Literal["build_down", "build_up", "net_cost"] | None = None
    # For Tariff Shift rules
    ts_from_chapter: str | None = None    # e.g. "any" or "28-38"
    ts_to_chapter: str | None = None
    ts_heading_level: Literal["chapter", "heading", "subheading"] | None = None
    ts_exceptions: list[str] = Field(default_factory=list)
    # For combined rules (both must pass)
    secondary_rule: "RooRule | None" = None


class RVCResult(BaseModel):
    method: str
    rvc_pct: float
    threshold_pct: float
    passes: bool
    non_originating_value_usd: float
    originating_value_usd: float
    transaction_value_usd: float
    net_cost_usd: float | None = None
    calculation_detail: str


class TariffShiftResult(BaseModel):
    passes: bool
    rule_text: str
    input_hs_codes: list[str]
    output_hs_code: str
    shift_level: str
    exceptions_triggered: list[str] = Field(default_factory=list)
    detail: str


class WhollyObtainedResult(BaseModel):
    passes: bool
    category: str | None
    production_country: str
    detail: str


class AgreementDetermination(BaseModel):
    agreement_code: str
    rule_applied: RuleType
    rule_text: str
    result: DeterminationResult
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    rvc_result: RVCResult | None = None
    ts_result: TariffShiftResult | None = None
    wo_result: WhollyObtainedResult | None = None
    preferential_rate: str | None = None
    mfn_rate: str | None = None
    savings_per_unit: float | None = None


class EngineOutput(BaseModel):
    product_hs: str
    production_country: str
    agreements_evaluated: list[str]
    determinations: list[AgreementDetermination]
    best_agreement: str | None = None
    best_saving_usd: float | None = None
    needs_human_review: bool = False
    review_reasons: list[str] = Field(default_factory=list)

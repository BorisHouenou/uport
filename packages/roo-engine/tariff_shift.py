"""
Tariff Shift (TS) / Change in Tariff Classification (CTC) calculator.

Three levels of shift specificity:
  • CC  — Change in Chapter (2-digit): all non-originating inputs must be
           classified in a different HS chapter than the output good.
  • CTH — Change in Tariff Heading (4-digit): inputs must differ at heading level.
  • CTSH— Change in Tariff Sub-Heading (6-digit): inputs must differ at sub-heading.

Exceptions: certain HS codes may be exempt from the shift requirement
(i.e. they are allowed to be the same chapter/heading as the output).
"""
from __future__ import annotations

import re

from models import BOMLine, TariffShiftResult


def _hs_chapter(hs: str) -> str:
    return hs[:2].zfill(2)


def _hs_heading(hs: str) -> str:
    return hs[:4].zfill(4)


def _hs_subheading(hs: str) -> str:
    return hs[:6].zfill(6)


def _normalize(hs: str) -> str:
    return re.sub(r"[.\s]", "", hs)


def _codes_from_non_originating(bom: list[BOMLine]) -> list[str]:
    """Extract HS codes from non-originating (or unknown) BOM lines."""
    codes = []
    for line in bom:
        if line.is_originating is True:
            continue  # originating materials are exempt from TS requirement
        if line.hs_code:
            codes.append(_normalize(line.hs_code))
    return codes


def check_change_in_chapter(
    bom: list[BOMLine],
    output_hs: str,
    exceptions: list[str] | None = None,
    rule_text: str = "CC — Change in Chapter",
) -> TariffShiftResult:
    """
    All non-originating inputs must be in a different HS chapter than the output.
    """
    out_chapter = _hs_chapter(_normalize(output_hs))
    input_codes = _codes_from_non_originating(bom)
    exceptions = [_normalize(e) for e in (exceptions or [])]
    violations = []

    for code in input_codes:
        in_chapter = _hs_chapter(code)
        if in_chapter == out_chapter:
            # Check if this code is in the exceptions list
            if not any(code.startswith(_hs_chapter(e)) for e in exceptions):
                violations.append(code)

    passes = len(violations) == 0
    detail = (
        f"CC check: output chapter {out_chapter}. "
        + (f"PASS — all {len(input_codes)} non-originating inputs are from different chapters."
           if passes
           else f"FAIL — {len(violations)} input(s) share chapter {out_chapter}: {violations}")
    )
    return TariffShiftResult(
        passes=passes,
        rule_text=rule_text,
        input_hs_codes=input_codes,
        output_hs_code=_normalize(output_hs),
        shift_level="chapter",
        exceptions_triggered=[c for c in violations if any(c.startswith(_hs_chapter(e)) for e in exceptions)],
        detail=detail,
    )


def check_change_in_heading(
    bom: list[BOMLine],
    output_hs: str,
    exceptions: list[str] | None = None,
    rule_text: str = "CTH — Change in Tariff Heading",
) -> TariffShiftResult:
    """
    All non-originating inputs must be in a different HS heading (4-digit) than the output.
    """
    out_heading = _hs_heading(_normalize(output_hs))
    input_codes = _codes_from_non_originating(bom)
    exceptions = [_normalize(e) for e in (exceptions or [])]
    violations = []

    for code in input_codes:
        in_heading = _hs_heading(code)
        if in_heading == out_heading:
            if code not in exceptions and not any(code.startswith(e[:4]) for e in exceptions):
                violations.append(code)

    passes = len(violations) == 0
    detail = (
        f"CTH check: output heading {out_heading}. "
        + (f"PASS — all {len(input_codes)} non-originating inputs shift at heading level."
           if passes
           else f"FAIL — {len(violations)} input(s) share heading {out_heading}: {violations}")
    )
    return TariffShiftResult(
        passes=passes,
        rule_text=rule_text,
        input_hs_codes=input_codes,
        output_hs_code=_normalize(output_hs),
        shift_level="heading",
        exceptions_triggered=[],
        detail=detail,
    )


def check_change_in_subheading(
    bom: list[BOMLine],
    output_hs: str,
    exceptions: list[str] | None = None,
    rule_text: str = "CTSH — Change in Tariff Sub-Heading",
) -> TariffShiftResult:
    """
    All non-originating inputs must be in a different HS sub-heading (6-digit).
    """
    out_sub = _hs_subheading(_normalize(output_hs))
    input_codes = _codes_from_non_originating(bom)
    exceptions = [_normalize(e) for e in (exceptions or [])]
    violations = []

    for code in input_codes:
        in_sub = _hs_subheading(code)
        if in_sub == out_sub and code not in exceptions:
            violations.append(code)

    passes = len(violations) == 0
    detail = (
        f"CTSH check: output sub-heading {out_sub}. "
        + (f"PASS — all {len(input_codes)} non-originating inputs shift at sub-heading level."
           if passes
           else f"FAIL — {len(violations)} input(s) share sub-heading {out_sub}: {violations}")
    )
    return TariffShiftResult(
        passes=passes,
        rule_text=rule_text,
        input_hs_codes=input_codes,
        output_hs_code=_normalize(output_hs),
        shift_level="subheading",
        exceptions_triggered=[],
        detail=detail,
    )


def evaluate_tariff_shift(
    bom: list[BOMLine],
    output_hs: str,
    shift_level: str,
    exceptions: list[str] | None = None,
    rule_text: str = "",
) -> TariffShiftResult:
    """Dispatch to the correct shift level check."""
    level = shift_level.lower()
    if level in ("chapter", "cc"):
        return check_change_in_chapter(bom, output_hs, exceptions, rule_text or "CC")
    elif level in ("heading", "cth"):
        return check_change_in_heading(bom, output_hs, exceptions, rule_text or "CTH")
    elif level in ("subheading", "ctsh"):
        return check_change_in_subheading(bom, output_hs, exceptions, rule_text or "CTSH")
    else:
        raise ValueError(f"Unknown tariff shift level: {shift_level!r}")

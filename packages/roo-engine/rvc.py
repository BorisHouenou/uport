"""
Regional Value Content (RVC) calculator.

Supports three CUSMA/WTO-standard methods:
  • Build-Down  (BD):  RVC = (TV - VNM) / TV × 100
  • Build-Up    (BU):  RVC = VOM / TV × 100
  • Net Cost    (NC):  RVC = (NC - VNM) / NC × 100

Where:
  TV  = transaction value of the good (ex-works / FOB)
  NC  = net cost of the good (TV minus specified costs)
  VNM = value of non-originating materials
  VOM = value of originating materials
"""
from __future__ import annotations

from models import BOMLine, RVCResult


def _split_bom(bom: list[BOMLine]) -> tuple[float, float]:
    """Return (originating_usd, non_originating_usd) from BOM lines."""
    orig = 0.0
    non_orig = 0.0
    for line in bom:
        cost = (line.unit_cost_usd or line.unit_cost) * line.quantity
        if line.is_originating is True:
            orig += cost
        elif line.is_originating is False:
            non_orig += cost
        else:
            # Unknown origin — conservatively treat as non-originating
            non_orig += cost
    return orig, non_orig


def calculate_build_down(
    bom: list[BOMLine],
    transaction_value_usd: float,
    threshold_pct: float = 40.0,
) -> RVCResult:
    """
    Build-Down: RVC = (TV - VNM) / TV × 100
    Most common method under CUSMA for manufacturing goods.
    Minimum threshold is typically 40% (CUSMA) or 45% (CETA).
    """
    _, vnm = _split_bom(bom)
    if transaction_value_usd <= 0:
        return RVCResult(
            method="build_down",
            rvc_pct=0.0,
            threshold_pct=threshold_pct,
            passes=False,
            non_originating_value_usd=vnm,
            originating_value_usd=0.0,
            transaction_value_usd=transaction_value_usd,
            calculation_detail="Transaction value must be > 0",
        )
    rvc = ((transaction_value_usd - vnm) / transaction_value_usd) * 100
    vom = transaction_value_usd - vnm
    return RVCResult(
        method="build_down",
        rvc_pct=round(rvc, 2),
        threshold_pct=threshold_pct,
        passes=rvc >= threshold_pct,
        non_originating_value_usd=round(vnm, 2),
        originating_value_usd=round(vom, 2),
        transaction_value_usd=round(transaction_value_usd, 2),
        calculation_detail=(
            f"RVC = (TV − VNM) / TV × 100 "
            f"= ({transaction_value_usd:.2f} − {vnm:.2f}) / {transaction_value_usd:.2f} × 100 "
            f"= {rvc:.2f}%  (threshold: {threshold_pct}%)"
        ),
    )


def calculate_build_up(
    bom: list[BOMLine],
    transaction_value_usd: float,
    threshold_pct: float = 40.0,
) -> RVCResult:
    """
    Build-Up: RVC = VOM / TV × 100
    Preferred when the good has a high proportion of originating materials.
    """
    vom, _ = _split_bom(bom)
    if transaction_value_usd <= 0:
        return RVCResult(
            method="build_up",
            rvc_pct=0.0,
            threshold_pct=threshold_pct,
            passes=False,
            non_originating_value_usd=0.0,
            originating_value_usd=vom,
            transaction_value_usd=transaction_value_usd,
            calculation_detail="Transaction value must be > 0",
        )
    rvc = (vom / transaction_value_usd) * 100
    vnm = transaction_value_usd - vom
    return RVCResult(
        method="build_up",
        rvc_pct=round(rvc, 2),
        threshold_pct=threshold_pct,
        passes=rvc >= threshold_pct,
        non_originating_value_usd=round(vnm, 2),
        originating_value_usd=round(vom, 2),
        transaction_value_usd=round(transaction_value_usd, 2),
        calculation_detail=(
            f"RVC = VOM / TV × 100 "
            f"= {vom:.2f} / {transaction_value_usd:.2f} × 100 "
            f"= {rvc:.2f}%  (threshold: {threshold_pct}%)"
        ),
    )


def calculate_net_cost(
    bom: list[BOMLine],
    transaction_value_usd: float,
    net_cost_usd: float,
    threshold_pct: float = 35.0,
) -> RVCResult:
    """
    Net Cost: RVC = (NC - VNM) / NC × 100
    Required for certain automotive goods under CUSMA (threshold 35–45%).
    Net Cost = TV minus royalties, sales promotion, packing/shipping, and
    non-allowable interest costs.
    """
    _, vnm = _split_bom(bom)
    if net_cost_usd <= 0:
        return RVCResult(
            method="net_cost",
            rvc_pct=0.0,
            threshold_pct=threshold_pct,
            passes=False,
            non_originating_value_usd=vnm,
            originating_value_usd=0.0,
            transaction_value_usd=transaction_value_usd,
            net_cost_usd=net_cost_usd,
            calculation_detail="Net cost must be > 0",
        )
    rvc = ((net_cost_usd - vnm) / net_cost_usd) * 100
    vom = net_cost_usd - vnm
    return RVCResult(
        method="net_cost",
        rvc_pct=round(rvc, 2),
        threshold_pct=threshold_pct,
        passes=rvc >= threshold_pct,
        non_originating_value_usd=round(vnm, 2),
        originating_value_usd=round(vom, 2),
        transaction_value_usd=round(transaction_value_usd, 2),
        net_cost_usd=round(net_cost_usd, 2),
        calculation_detail=(
            f"RVC = (NC − VNM) / NC × 100 "
            f"= ({net_cost_usd:.2f} − {vnm:.2f}) / {net_cost_usd:.2f} × 100 "
            f"= {rvc:.2f}%  (threshold: {threshold_pct}%)"
        ),
    )


def best_rvc_method(
    bom: list[BOMLine],
    transaction_value_usd: float,
    threshold_pct: float = 40.0,
    net_cost_usd: float | None = None,
) -> RVCResult:
    """
    Try all available methods and return the one most favourable to the exporter.
    Useful when the agreement permits the exporter to choose the method.
    """
    results = [
        calculate_build_down(bom, transaction_value_usd, threshold_pct),
        calculate_build_up(bom, transaction_value_usd, threshold_pct),
    ]
    if net_cost_usd is not None:
        results.append(calculate_net_cost(bom, transaction_value_usd, net_cost_usd, threshold_pct))

    # Prefer passing results; among those, highest RVC%
    passing = [r for r in results if r.passes]
    if passing:
        return max(passing, key=lambda r: r.rvc_pct)
    # No method passes — return the one closest to threshold
    return max(results, key=lambda r: r.rvc_pct)

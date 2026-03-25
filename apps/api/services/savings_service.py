"""Savings / ROI computation service."""
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select, extract, case, cast, Float
from sqlalchemy.ext.asyncio import AsyncSession

from models import OriginDetermination, Shipment, Certificate


async def get_savings_summary(db: AsyncSession, org_id: uuid.UUID) -> dict[str, Any]:
    """
    Return a summary of tariff savings for the org:
      - KPIs (total savings YTD, certificates issued, avg saving/shipment, compliance rate)
      - Monthly savings trend (last 6 months)
      - Savings by agreement
      - Annual projection
    """
    # ── KPIs ──────────────────────────────────────────────────────────────────
    now = datetime.now(timezone.utc)
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # Total savings YTD — sum savings_per_unit * shipment_value_usd proxy
    # savings_per_unit is expressed as a fraction saved (mfn_rate - pref_rate).
    # When populated it holds absolute dollar savings per unit. We sum it directly.
    savings_q = await db.execute(
        select(func.coalesce(func.sum(cast(OriginDetermination.savings_per_unit, Float)), 0.0))
        .join(Shipment, OriginDetermination.shipment_id == Shipment.id)
        .where(Shipment.org_id == org_id)
        .where(OriginDetermination.result == "pass")
        .where(OriginDetermination.created_at >= year_start)
    )
    total_savings_ytd: float = float(savings_q.scalar_one())

    # Certificates issued YTD
    certs_q = await db.execute(
        select(func.count(Certificate.id))
        .join(Shipment, Certificate.shipment_id == Shipment.id)
        .where(Shipment.org_id == org_id)
        .where(Certificate.issued_at >= year_start)
        .where(Certificate.status == "issued")
    )
    certs_issued: int = certs_q.scalar_one()

    # Total passing shipments YTD (for avg calculation + compliance rate)
    det_stats_q = await db.execute(
        select(
            func.count(OriginDetermination.id).label("total"),
            func.sum(
                case((OriginDetermination.result == "pass", 1), else_=0)
            ).label("passing"),
        )
        .join(Shipment, OriginDetermination.shipment_id == Shipment.id)
        .where(Shipment.org_id == org_id)
        .where(OriginDetermination.created_at >= year_start)
    )
    det_stats = det_stats_q.one()
    total_dets: int = det_stats.total or 0
    passing_dets: int = int(det_stats.passing or 0)

    avg_saving = (total_savings_ytd / passing_dets) if passing_dets else 0.0
    compliance_rate = round((passing_dets / total_dets * 100), 1) if total_dets else 0.0

    # ── Monthly trend (last 6 months) ─────────────────────────────────────────
    monthly_q = await db.execute(
        select(
            extract("year",  OriginDetermination.created_at).label("yr"),
            extract("month", OriginDetermination.created_at).label("mo"),
            func.coalesce(func.sum(cast(OriginDetermination.savings_per_unit, Float)), 0.0).label("savings"),
            func.count(OriginDetermination.shipment_id.distinct()).label("shipments"),
        )
        .join(Shipment, OriginDetermination.shipment_id == Shipment.id)
        .where(Shipment.org_id == org_id)
        .where(OriginDetermination.result == "pass")
        .where(OriginDetermination.created_at >= _months_ago(now, 6))
        .group_by("yr", "mo")
        .order_by("yr", "mo")
    )
    monthly_rows = monthly_q.all()

    MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly = [
        {
            "month": MONTH_ABBR[int(r.mo) - 1],
            "savings": round(float(r.savings), 2),
            "shipments": int(r.shipments),
        }
        for r in monthly_rows
    ]

    # ── By agreement ──────────────────────────────────────────────────────────
    by_agr_q = await db.execute(
        select(
            OriginDetermination.agreement_code,
            OriginDetermination.agreement_name,
            func.coalesce(func.sum(cast(OriginDetermination.savings_per_unit, Float)), 0.0).label("savings"),
            func.count(OriginDetermination.shipment_id.distinct()).label("shipments"),
        )
        .join(Shipment, OriginDetermination.shipment_id == Shipment.id)
        .where(Shipment.org_id == org_id)
        .where(OriginDetermination.result == "pass")
        .where(OriginDetermination.created_at >= year_start)
        .group_by(OriginDetermination.agreement_code, OriginDetermination.agreement_name)
        .order_by(func.sum(cast(OriginDetermination.savings_per_unit, Float)).desc())
    )
    by_agr_rows = by_agr_q.all()

    by_agreement = [
        {
            "agreement": r.agreement_code,
            "agreement_name": r.agreement_name,
            "savings": round(float(r.savings), 2),
            "shipments": int(r.shipments),
        }
        for r in by_agr_rows
    ]

    # ── Annual projection ─────────────────────────────────────────────────────
    months_elapsed = now.month + (now.day / 30)
    annual_projection = round((total_savings_ytd / months_elapsed * 12), 2) if months_elapsed else 0.0

    return {
        "kpis": {
            "total_savings_ytd": round(total_savings_ytd, 2),
            "certificates_issued": certs_issued,
            "avg_saving_per_shipment": round(avg_saving, 2),
            "compliance_rate": compliance_rate,
        },
        "monthly": monthly,
        "by_agreement": by_agreement,
        "annual_projection": annual_projection,
        "currency": "USD",
    }


def _months_ago(now: datetime, n: int) -> datetime:
    month = now.month - n
    year = now.year + month // 12
    month = month % 12 or 12
    return now.replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)

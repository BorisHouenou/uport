"""Trade agreement and RoO rules DB service layer."""
import uuid

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.agreement import TradeAgreement, RooRule


async def get_applicable_agreements(
    db: AsyncSession,
    origin_country: str | None,
    destination_country: str | None,
) -> dict:
    query = select(TradeAgreement).where(TradeAgreement.is_active == True)
    if origin_country and destination_country:
        # Filter to agreements where both countries are parties
        # Using array contains operator for PostgreSQL ARRAY type
        from sqlalchemy import cast, String
        from sqlalchemy.dialects.postgresql import ARRAY
        query = query.where(
            TradeAgreement.parties.contains([origin_country.upper()])
        ).where(
            TradeAgreement.parties.contains([destination_country.upper()])
        )
    result = await db.execute(query)
    agreements = result.scalars().all()
    return {"agreements": agreements, "total": len(agreements)}


async def get_rules_for_agreement(
    db: AsyncSession,
    agreement_code: str,
    hs_code: str | None = None,
) -> dict:
    # First get the agreement
    ag_result = await db.execute(
        select(TradeAgreement).where(TradeAgreement.code == agreement_code.lower())
    )
    agreement = ag_result.scalar_one_or_none()
    if not agreement:
        return {"agreement_code": agreement_code, "rules": [], "total": 0}

    query = select(RooRule).where(RooRule.agreement_id == agreement.id)
    if hs_code:
        cleaned = hs_code.replace(".", "").strip()
        heading = cleaned[:4]
        chapter = cleaned[:2]
        query = query.where(
            or_(
                RooRule.hs_subheading == cleaned[:6],
                RooRule.hs_heading == heading,
                RooRule.hs_chapter == chapter,
            )
        )
    result = await db.execute(query)
    rules = result.scalars().all()
    return {"agreement_code": agreement_code, "rules": rules, "total": len(rules)}

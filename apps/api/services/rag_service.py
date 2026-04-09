"""Inline RAG compliance assistant — uses Anthropic API directly."""
from __future__ import annotations

import json
import uuid
from typing import AsyncIterator

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# ── Built-in trade agreement knowledge ────────────────────────────────────────
_KNOWLEDGE = """
CUSMA (Canada-United States-Mexico Agreement) / USMCA:
- Regional Value Content (RVC) for most goods: ≥35% Build-Down or ≥45% Net-Cost method
- Passenger vehicles (HS 8703): ≥75% RVC (phased in), steel/aluminum content rules, labor value content (LVC) ≥25%
- Light trucks (HS 8704): ≥75% RVC
- Auto parts (HS 8708): ≥65–75% RVC depending on part type
- Tariff shift rules: Change in Tariff Classification (CTC) from any heading outside the chapter
- De minimis: up to 10% of transaction value for non-originating materials that don't undergo tariff shift
- Wholly obtained goods (e.g., agricultural): 100% originating
- Chapters 1–24 (agricultural): specific rules per product, many requiring domestic production
- Textiles/Apparel: yarn-forward rule — fiber, yarn, and fabric must originate in CUSMA territory
- Steel/Aluminum: must be melted and poured in North America for automotive
- Labor Value Content (LVC): ≥25% of vehicle value from workers earning ≥US$16/hour
- Certificate of Origin: exporter self-certifies; no official form required (unlike old NAFTA CO)
- Dispute settlement: Chapter 31 for state-to-state; Chapter 14 for investor-state (limited)
- Rules of Origin: Chapter 4 and Annex 4-B (product-specific rules)
- Tariff elimination: most goods at 0% immediately; staged elimination for sensitive sectors
- Country of origin marking: goods must be marked with country of origin (Article 7.9)

CETA (Canada-European Union Comprehensive Economic and Trade Agreement):
- RVC threshold: generally ≥50% for industrial goods (EXW price basis)
- Tariff shift: primarily CTH (Change of Tariff Heading) for most goods
- Wholly obtained: applies to fish, agricultural products entirely produced in Canada or EU
- Cumulation: bilateral cumulation allowed (Canadian + EU content counts together)
- EUR.1 movement certificate or exporter's statement for shipments ≤€6,000 (approved exporters unlimited)
- Vehicles (HS 8703): 50% RVC or tariff shift from outside HS 87
- Chemicals: CTH or 50% RVC depending on specific heading
- Textiles: double transformation rule (fabric must be woven/knitted in Canada or EU)
- Agricultural: TRQs (tariff rate quotas) for many sensitive products (cheese, beef)
- Provisional application since September 2017; investment chapter pending EU ratification
- Rules of Origin: Protocol on Rules of Origin and Origin Procedures
- Tolerance rule: up to 10% (15% for textiles) of ex-works price in non-originating materials
- Direct transport rule: goods must be transported directly (no reworking in third country)
- Proof of origin: origin declaration on invoice or EUR.1 certificate

CPTPP (Comprehensive and Progressive Agreement for Trans-Pacific Partnership):
- Members: Canada, Australia, Brunei, Chile, Japan, Malaysia, Mexico, New Zealand, Peru, Singapore, Vietnam
- RVC: generally 40–45% depending on method (FOB or net cost)
- Tariff shift: CTH or CTSH (Change of Tariff Sub-Heading) for most goods
- Vehicles (HS 8703): 45% RVC (Japan-Canada trade)
- Electronics: generally CTH from outside HS 84–85, or 40% RVC
- Chemicals: RVC 40% or specific chemical reaction rule
- Accumulation: allows content from any CPTPP member to count as originating
- De minimis: 10% of FOB value for non-originating materials
- Textile: yarn-forward with some tariff preference level (TPL) exceptions
- PSR (Product-Specific Rules): Annex 3-D contains rules for each HS chapter
- Entry into force for Canada: December 30, 2018
- Certificate of origin: self-certification by exporter, producer, or importer

CKFTA (Canada-Korea Free Trade Agreement):
- RVC: generally 35–40% depending on method
- Tariff shift: CTH for most manufactured goods
- Vehicles: 35% RVC (lower than CUSMA/CPTPP)
- Bilateral cumulation only
"""

_SYSTEM_PROMPT = f"""You are a trade compliance expert assistant for Uportai, specializing in Rules of Origin (RoO) under CUSMA, CETA, CPTPP, and CKFTA.

You have access to the following trade agreement knowledge:

{_KNOWLEDGE}

When answering:
1. Be precise and cite the relevant agreement, chapter, or article when possible
2. Distinguish between different RVC methods (Build-Down, Net-Cost, Transaction Value)
3. Clarify when rules depend on the specific HS code
4. If unsure about a very specific provision, say so and recommend consulting the official agreement text
5. Keep answers concise but complete — 2-4 paragraphs typically

Format citations as: [CUSMA Art. 4.X], [CETA Protocol Art. X], [CPTPP Annex 3-D], etc.
"""


async def stream_compliance_answer(
    messages: list[dict],
    org_id: str | None = None,
    agreement_filter: list[str] | None = None,
) -> AsyncIterator[str]:
    """Stream compliance answer using Anthropic API."""
    import anthropic as anthropic_lib

    api_key = settings.anthropic_api_key
    if not api_key:
        yield json.dumps({"type": "text", "text": "The compliance assistant requires an Anthropic API key. Please contact your administrator."})
        return

    # Build system prompt with agreement filter
    system = _SYSTEM_PROMPT
    if agreement_filter:
        system += f"\n\nFocus your answer specifically on these agreements: {', '.join(a.upper() for a in agreement_filter)}."

    # Filter to last N messages to stay within context
    recent = messages[-10:]

    client = anthropic_lib.AsyncAnthropic(api_key=api_key)

    try:
        async with client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=recent,
        ) as stream:
            async for text in stream.text_stream:
                yield json.dumps({"type": "text", "text": text})

        citations = _extract_citations(messages[-1].get("content", "") if messages else "", agreement_filter)
        if citations:
            yield json.dumps({"type": "citations", "citations": citations})

    except anthropic_lib.APIError as e:
        logger.error("anthropic_api_error", error=str(e))
        yield json.dumps({"type": "text", "text": f"API error: {e.message if hasattr(e, 'message') else str(e)}"})
    except Exception as e:
        logger.error("rag_stream_error", error=str(e))
        yield json.dumps({"type": "text", "text": "An error occurred while processing your question. Please try again."})


def _extract_citations(question: str, agreement_filter: list[str] | None) -> list[dict]:
    """Generate relevant citation hints based on the question topic."""
    q = question.lower()
    citations = []

    if any(w in q for w in ["vehicle", "car", "automotive", "passenger"]):
        if not agreement_filter or "cusma" in agreement_filter:
            citations.append({"agreement": "CUSMA", "reference": "Annex 4-B, HS 8703", "url": None})
        if not agreement_filter or "cptpp" in agreement_filter:
            citations.append({"agreement": "CPTPP", "reference": "Annex 3-D, HS 8703", "url": None})

    if any(w in q for w in ["rvc", "regional value", "value content", "threshold"]):
        if not agreement_filter or "cusma" in agreement_filter:
            citations.append({"agreement": "CUSMA", "reference": "Article 4.5 — Regional Value Content", "url": None})
        if not agreement_filter or "ceta" in agreement_filter:
            citations.append({"agreement": "CETA", "reference": "Protocol on Rules of Origin, Art. 6", "url": None})

    if any(w in q for w in ["textile", "apparel", "fabric", "yarn", "fiber"]):
        if not agreement_filter or "cusma" in agreement_filter:
            citations.append({"agreement": "CUSMA", "reference": "Chapter 6 — Textile and Apparel Goods", "url": None})

    if any(w in q for w in ["tariff shift", "ctc", "cth", "ctsh", "classification"]):
        if not agreement_filter or "cusma" in agreement_filter:
            citations.append({"agreement": "CUSMA", "reference": "Article 4.2 — Originating Goods", "url": None})

    if any(w in q for w in ["wholly obtained", "wholly produced", "natural"]):
        citations.append({"agreement": "CUSMA/CETA/CPTPP", "reference": "Wholly Obtained rules — Chapter 4 / Protocol Art. 4", "url": None})

    return citations


async def save_chat_turn(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    user_content: str,
    assistant_content: str,
    citations: list | None = None,
) -> None:
    """Persist a chat turn to chat_messages table."""
    try:
        from models.chat import ChatMessage
        for role, content in [("user", user_content), ("assistant", assistant_content)]:
            msg = ChatMessage(
                id=uuid.uuid4(),
                org_id=uuid.UUID(org_id),
                user_id=user_id,
                role=role,
                content=content,
                citations=citations if role == "assistant" else None,
            )
            db.add(msg)
        await db.commit()
    except Exception as e:
        logger.warning("chat_persist_failed", error=str(e))


async def get_chat_history(db: AsyncSession, user_id: str, limit: int = 50) -> dict:
    """Retrieve recent chat history."""
    try:
        from models.chat import ChatMessage
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        rows = result.scalars().all()
        return {
            "messages": [
                {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat() if m.created_at else None}
                for m in reversed(rows)
            ]
        }
    except Exception as e:
        logger.warning("chat_history_failed", error=str(e))
        return {"messages": []}

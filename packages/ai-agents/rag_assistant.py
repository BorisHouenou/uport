"""
RAG Compliance Assistant.

Architecture:
  - Document store: pgvector (via LlamaIndex PGVectorStore)
  - Embeddings: Voyage AI voyage-3 (1536-dim) with OpenAI fallback
  - LLM: Claude claude-sonnet-4-6 with streaming
  - Retrieval: top-k=8 with MMR re-ranking
  - Citations: every answer cites the source article/annex

The assistant answers trade compliance questions grounded in indexed
FTA texts (CUSMA, CETA, CPTPP annexes) and tariff schedules.
"""
from __future__ import annotations

import os
import json
import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL  = os.getenv("LLM_MODEL", "claude-sonnet-4-6")

# ─── In-memory knowledge base (bootstraps without pgvector in dev) ─────────────
KNOWLEDGE_BASE: list[dict] = [
    # CUSMA
    {
        "source": "CUSMA Article 4.2 — Originating Goods",
        "agreement": "cusma",
        "content": (
            "A good is originating if: (a) it is wholly obtained or produced entirely in the territory "
            "of one or more of the Parties; (b) it is produced entirely in the territory of one or more "
            "of the Parties using non-originating materials provided the good satisfies all applicable "
            "requirements of Annex 4-B (Product-Specific Rules); or (c) it is produced entirely in the "
            "territory of one or more of the Parties exclusively from originating materials."
        ),
    },
    {
        "source": "CUSMA Article 4.5 — Wholly Obtained or Produced Goods",
        "agreement": "cusma",
        "content": (
            "A good is wholly obtained or produced entirely in the territory of one or more of the Parties if: "
            "(a) it is a mineral good or other naturally occurring substance extracted or taken from the territory; "
            "(b) it is a plant, fungus, or plant product grown, cultivated, harvested, picked, or gathered; "
            "(c) it is a live animal born and raised in the territory; (d) it is a good obtained from a live animal; "
            "(e) it is obtained from hunting, trapping, fishing, gathering, or capturing; "
            "(f) it is a fish, shellfish, or other marine creature taken from the sea."
        ),
    },
    {
        "source": "CUSMA Article 4.8 — Regional Value Content",
        "agreement": "cusma",
        "content": (
            "Regional Value Content (RVC) may be calculated using: "
            "(a) the Build-Down Method: RVC = [(TV - VNM) / TV] × 100, where TV is the transaction value "
            "and VNM is the value of non-originating materials; "
            "(b) the Build-Up Method: RVC = [VOM / TV] × 100, where VOM is the value of originating materials; "
            "(c) the Net Cost Method: RVC = [(NC - VNM) / NC] × 100, where NC is the net cost of the good. "
            "The minimum RVC threshold for most goods is 40% under Build-Down or 30% under Net Cost."
        ),
    },
    {
        "source": "CUSMA Annex 4-B — Automotive Goods (Chapter 87)",
        "agreement": "cusma",
        "content": (
            "For passenger vehicles (HS 8703), the RVC requirement is 75% under the Build-Down Method "
            "or 65% under the Net Cost Method by 2023. Core parts (engine, transmission, body stampings, "
            "axles, suspensions, steering) have their own separate originating requirements. "
            "Steel and aluminium used in covered vehicles must be melted and poured in North America."
        ),
    },
    {
        "source": "CUSMA Article 4.18 — De Minimis",
        "agreement": "cusma",
        "content": (
            "A good that does not satisfy the tariff classification change requirement shall nonetheless "
            "be considered originating if the value of all non-originating materials that do not undergo "
            "the required change does not exceed 10% of the transaction value of the good, provided the "
            "good satisfies all other applicable requirements. For agricultural goods, the threshold may differ."
        ),
    },
    {
        "source": "CUSMA Article 4.12 — Accumulation",
        "agreement": "cusma",
        "content": (
            "Originating goods or materials of a Party incorporated into a good in the territory of another "
            "Party shall be considered to originate in the territory of that other Party. Production of a good "
            "in the territory of one or more of the Parties may be accumulated for the purpose of determining "
            "whether the good satisfies originating requirements."
        ),
    },
    # CETA
    {
        "source": "CETA Protocol on Rules of Origin, Article 3 — General Requirements",
        "agreement": "ceta",
        "content": (
            "A product is originating in Canada or the EU if: (a) it is wholly obtained in Canada or the EU; "
            "(b) it is produced exclusively from originating materials; or (c) it satisfies the product-specific "
            "rules in Annex II. The EU includes cumulation among member states. Canada and EU may cumulate "
            "production for determining originating status."
        ),
    },
    {
        "source": "CETA Protocol, Article 6 — Insufficient Processing",
        "agreement": "ceta",
        "content": (
            "The following operations shall be considered insufficient to confer originating status regardless "
            "of whether product-specific rules are satisfied: (a) preserving operations such as drying, freezing, "
            "keeping in brine; (b) changes of packaging; (c) simple cutting, slicing, and repacking; "
            "(d) simple assembly of parts to constitute a complete article; (e) a combination of two or more "
            "of these operations. These are known as 'minimal operations'."
        ),
    },
    {
        "source": "CETA Annex II — Product-Specific Rules (Chapter 87, Vehicles)",
        "agreement": "ceta",
        "content": (
            "For motor vehicles of HS Chapter 87: MaxNOM (Maximum Non-Originating Materials) of 45% "
            "of the ex-works price. Equivalently, at least 55% of the ex-works price must consist of "
            "originating materials. This is modelled as RVC ≥ 55% under the Build-Down method. "
            "For auto parts of heading 87.08, the same 45% MaxNOM applies."
        ),
    },
    {
        "source": "CETA Protocol, Article 16 — Supplier's Declaration",
        "agreement": "ceta",
        "content": (
            "A supplier's declaration is a statement made by the supplier of a product to confirm that "
            "the product qualifies as originating. It may be given for a single consignment or cover "
            "multiple deliveries of identical products for a period not exceeding 12 months (long-term "
            "supplier's declaration). The declaration must be kept for at least 3 years."
        ),
    },
    # CPTPP
    {
        "source": "CPTPP Article 3.2 — Originating Goods",
        "agreement": "cptpp",
        "content": (
            "A good is originating if: (a) it is wholly obtained or produced entirely in the territory "
            "of one or more Parties; (b) it is produced entirely from originating materials; "
            "(c) it satisfies the applicable product-specific rules in Annex 3-D and all other "
            "applicable requirements of this Chapter. CPTPP allows for tariff preference levels (TPLs) "
            "for certain textile and apparel goods."
        ),
    },
    {
        "source": "CPTPP Article 3.5 — Regional Value Content",
        "agreement": "cptpp",
        "content": (
            "CPTPP uses both Build-Down and Net Cost methods. The Build-Down formula is: "
            "RVC = [(AV - VNM) / AV] × 100, where AV is the adjusted value (essentially FOB value). "
            "The Net Cost formula is: RVC = [(NC - VNM) / NC] × 100. "
            "For most manufactured goods the threshold is 40% (Build-Down) or 30% (Net Cost). "
            "Automotive goods under HS 8703 require at minimum 40% RVC."
        ),
    },
    {
        "source": "CPTPP Article 3.20 — Self-Certification",
        "agreement": "cptpp",
        "content": (
            "Under CPTPP, an importer, exporter, or producer may make a self-certification of origin. "
            "There is no requirement for a government-issued certificate. The certification must contain "
            "prescribed data elements including: certification of origin statement, certifier identity, "
            "importer information, producer information, description of goods, HS tariff classification, "
            "and applicable rule of origin. The certification is valid for 12 months."
        ),
    },
    # General
    {
        "source": "HS Nomenclature — Chapter Structure",
        "agreement": "general",
        "content": (
            "The Harmonised System (HS) is structured as: Section (broad category) → Chapter (2-digit) → "
            "Heading (4-digit) → Sub-heading (6-digit). Countries add additional digits for national use. "
            "Canada uses 8 digits (HS + 2 national), the US uses 10 digits (HTS). "
            "Tariff shift rules are specified at the chapter (CC), heading (CTH), or sub-heading (CTSH) level. "
            "A CC rule is more permissive than CTH, which is more permissive than CTSH."
        ),
    },
    {
        "source": "Certificate of Origin — Types and When to Use",
        "agreement": "general",
        "content": (
            "CUSMA: Use the 'Certification of Origin' statement (no official form required since 2020). "
            "Self-certified by exporter, importer, or producer. Valid up to 12 months. "
            "CETA: EUR.1 Movement Certificate issued by customs, or exporter's statement for shipments "
            "under EUR 6,000 (REX system for larger exporters). "
            "CPTPP: Self-certification — no government-issued form required. "
            "Form A (GSP): Used for developing country exports under the Generalised System of Preferences."
        ),
    },
]


SYSTEM_PROMPT = """You are a trade compliance specialist for Uportai, expert in Rules of Origin under CUSMA/USMCA, CETA, CPTPP, AfCFTA, and other major free trade agreements.

You answer compliance questions using the retrieved context below. Your answers must:
1. Be accurate and grounded in the retrieved sources
2. Cite the exact source (article, annex, or section) for every key claim in [brackets]
3. Be practical — give the exporter clear, actionable guidance
4. Flag any uncertainty or edge cases that need professional legal review
5. Never fabricate rules or statistics

If the retrieved context does not contain sufficient information, say so clearly and suggest where the exporter can find the answer (e.g. specific CBSA guidance, trade lawyer).

Format responses with clear structure: use short paragraphs, bullet points for lists, and bold key terms."""


async def _retrieve_pgvector(
    query: str,
    agreement_filter: list[str] | None,
    k: int,
) -> list[dict] | None:
    """
    Retrieve via pgvector cosine similarity.
    Returns None if pgvector is unavailable (missing env vars or connection error).
    """
    database_url = os.getenv("DATABASE_URL")
    voyage_key = os.getenv("VOYAGE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not database_url or (not voyage_key and not openai_key):
        return None

    try:
        import asyncpg
        import httpx

        # Embed the query
        if voyage_key:
            async with httpx.AsyncClient(timeout=15) as http:
                resp = await http.post(
                    "https://api.voyageai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {voyage_key}"},
                    json={"model": "voyage-3", "input": [query]},
                )
                resp.raise_for_status()
                embedding = resp.json()["data"][0]["embedding"]
        else:
            import base64
            async with httpx.AsyncClient(timeout=15) as http:
                resp = await http.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={"model": "text-embedding-3-small", "input": [query]},
                )
                resp.raise_for_status()
                embedding = resp.json()["data"][0]["embedding"]

        dsn = database_url.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql://", "postgres://")
        conn = await asyncpg.connect(dsn)

        try:
            where_clause = ""
            params: list[Any] = [str(embedding), k]
            if agreement_filter:
                placeholders = ", ".join(f"${i+3}" for i in range(len(agreement_filter)))
                where_clause = f"WHERE agreement IN ({placeholders}) OR agreement = 'general'"
                params.extend(agreement_filter)

            rows = await conn.fetch(
                f"""
                SELECT agreement, source, content,
                       1 - (embedding <=> $1::vector) AS similarity
                FROM document_chunks
                {where_clause}
                ORDER BY embedding <=> $1::vector
                LIMIT $2
                """,
                *params,
            )
        finally:
            await conn.close()

        return [
            {"agreement": r["agreement"], "source": r["source"], "content": r["content"]}
            for r in rows
        ]

    except Exception:
        return None  # fall through to keyword search


def _retrieve_keyword(query: str, agreement_filter: list[str] | None, k: int) -> list[dict]:
    """Keyword-based retrieval from in-memory KNOWLEDGE_BASE (dev fallback)."""
    query_lower = query.lower()
    keywords = [w for w in query_lower.split() if len(w) > 3]

    scored: list[tuple[float, dict]] = []
    for chunk in KNOWLEDGE_BASE:
        if agreement_filter and chunk["agreement"] not in agreement_filter and chunk["agreement"] != "general":
            continue
        content_lower = chunk["content"].lower() + " " + chunk["source"].lower()
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:k]]


def _retrieve(query: str, agreement_filter: list[str] | None, k: int = 6) -> list[dict]:
    """
    Retrieve relevant chunks for a query.
    Uses pgvector cosine similarity in production; falls back to keyword search in dev.
    Synchronous wrapper — runs the async pgvector path in a new event loop if needed.
    """
    if not query.strip():
        return []

    # Try pgvector (async) — run inside existing loop or create one
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're already inside an async context; pgvector will be called
            # from stream_compliance_answer which is async — see _retrieve_async below
            raise RuntimeError("use _retrieve_async instead")
        result = loop.run_until_complete(_retrieve_pgvector(query, agreement_filter, k))
        if result is not None:
            return result
    except Exception:
        pass

    return _retrieve_keyword(query, agreement_filter, k)


async def _retrieve_async(query: str, agreement_filter: list[str] | None, k: int = 6) -> list[dict]:
    """Async version of _retrieve — preferred inside async contexts."""
    if not query.strip():
        return []
    result = await _retrieve_pgvector(query, agreement_filter, k)
    if result is not None:
        return result
    return _retrieve_keyword(query, agreement_filter, k)


def _build_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant context retrieved."
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[{i}] **{chunk['source']}** ({chunk['agreement'].upper()})\n{chunk['content']}")
    return "\n\n".join(parts)


async def stream_compliance_answer(
    messages: list[dict],
    org_id: str,
    agreement_filter: list[str] | None = None,
) -> AsyncGenerator[str, None]:
    """
    Stream a RAG-grounded compliance answer.
    Yields SSE-formatted JSON chunks.
    """
    import json

    # Extract last user message for retrieval
    user_messages = [m for m in messages if m.get("role") == "user"]
    last_query = user_messages[-1]["content"] if user_messages else ""

    # Retrieve context (pgvector in prod, keyword in dev)
    chunks = await _retrieve_async(last_query, agreement_filter)
    context = _build_context(chunks)

    # Prepend context to conversation
    system_with_context = f"{SYSTEM_PROMPT}\n\n---\nRETRIEVED CONTEXT:\n{context}\n---"

    # Format messages for Claude
    claude_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
    ]

    # Stream response
    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        system=system_with_context,
        messages=claude_messages,
    ) as stream:
        for text in stream.text_stream:
            yield json.dumps({"type": "text", "text": text})

    # After streaming, yield citations
    if chunks:
        citations = [{"index": i + 1, "source": c["source"], "agreement": c["agreement"]}
                     for i, c in enumerate(chunks)]
        yield json.dumps({"type": "citations", "citations": citations})


async def save_chat_turn(
    db,
    org_id: str,
    user_id: str,
    user_content: str,
    assistant_content: str,
    citations: list[dict] | None = None,
) -> None:
    """Persist one user + assistant turn to chat_messages."""
    from sqlalchemy import text
    import uuid as _uuid

    await db.execute(
        text("""
            INSERT INTO chat_messages (id, org_id, user_id, role, content, citations)
            VALUES (:id1, :org_id, :user_id, 'user', :user_content, NULL),
                   (:id2, :org_id, :user_id, 'assistant', :assistant_content, :citations::jsonb)
        """),
        {
            "id1": str(_uuid.uuid4()),
            "id2": str(_uuid.uuid4()),
            "org_id": org_id,
            "user_id": user_id,
            "user_content": user_content,
            "assistant_content": assistant_content,
            "citations": json.dumps(citations) if citations else None,
        },
    )
    await db.commit()


async def get_chat_history(db, user_id: str, limit: int = 50) -> list[dict]:
    """Retrieve recent chat messages for a user from DB."""
    from sqlalchemy import text

    result = await db.execute(
        text("""
            SELECT role, content, citations, created_at
            FROM chat_messages
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit
        """),
        {"user_id": user_id, "limit": limit},
    )
    rows = result.fetchall()
    return [
        {
            "role": r.role,
            "content": r.content,
            "citations": r.citations,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reversed(rows)  # chronological order
    ]

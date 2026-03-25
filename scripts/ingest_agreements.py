#!/usr/bin/env python3
"""
Ingest FTA agreement texts into pgvector for RAG retrieval.

Usage:
    python scripts/ingest_agreements.py [--agreement cusma|ceta|cptpp|all]

The script:
1. Reads source texts from scripts/data/agreements/
2. Chunks each document into ~500-token segments with 50-token overlap
3. Generates embeddings via Voyage AI (voyage-3) or OpenAI fallback
4. Upserts into the document_chunks table (pgvector)

In development, the RAG assistant uses the in-memory KNOWLEDGE_BASE from
rag_assistant.py, so this script is only needed for production deployment.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Embedding providers
# ---------------------------------------------------------------------------

async def embed_voyage(texts: list[str]) -> list[list[float]]:
    """Embed using Voyage AI voyage-3 (1536-dim)."""
    import httpx
    api_key = os.environ["VOYAGE_API_KEY"]
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.voyageai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "voyage-3", "input": texts},
        )
        resp.raise_for_status()
        data = resp.json()
    return [d["embedding"] for d in data["data"]]


async def embed_openai(texts: list[str]) -> list[list[float]]:
    """Fallback: OpenAI text-embedding-3-small (1536-dim)."""
    import httpx
    api_key = os.environ["OPENAI_API_KEY"]
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "text-embedding-3-small", "input": texts},
        )
        resp.raise_for_status()
        data = resp.json()
    return [d["embedding"] for d in data["data"]]


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if os.environ.get("VOYAGE_API_KEY"):
        return await embed_voyage(texts)
    elif os.environ.get("OPENAI_API_KEY"):
        print("⚠  VOYAGE_API_KEY not set — falling back to OpenAI embeddings")
        return await embed_openai(texts)
    else:
        raise RuntimeError("Set VOYAGE_API_KEY or OPENAI_API_KEY to generate embeddings")


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into ~chunk_size word chunks with overlap."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


# ---------------------------------------------------------------------------
# Source data (canonical, versioned in-repo)
# ---------------------------------------------------------------------------

# In production, load from scripts/data/agreements/*.txt or a PDF parser.
# Here we seed from the same knowledge base used in dev for consistency.
def _load_knowledge_base() -> list[dict]:
    sys.path.insert(0, str(Path(__file__).parents[1] / "packages" / "ai-agents"))
    from rag_assistant import KNOWLEDGE_BASE
    return KNOWLEDGE_BASE


# ---------------------------------------------------------------------------
# Database upsert
# ---------------------------------------------------------------------------

async def upsert_chunks(chunks: list[dict[str, Any]]) -> None:
    """Upsert document chunks into pgvector table."""
    import asyncpg
    dsn = os.environ.get("DATABASE_URL", "postgresql://uportai:uportai@localhost:5432/uportai")
    # asyncpg uses postgres:// scheme
    dsn = dsn.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql://", "postgres://")

    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id          SERIAL PRIMARY KEY,
                agreement   TEXT NOT NULL,
                source      TEXT NOT NULL,
                content     TEXT NOT NULL,
                embedding   vector(1536),
                created_at  TIMESTAMPTZ DEFAULT now()
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS document_chunks_emb_idx ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")

        for chunk in chunks:
            await conn.execute(
                """
                INSERT INTO document_chunks (agreement, source, content, embedding)
                VALUES ($1, $2, $3, $4::vector)
                ON CONFLICT DO NOTHING
                """,
                chunk["agreement"],
                chunk["source"],
                chunk["content"],
                str(chunk["embedding"]),
            )
        print(f"  ✓ Upserted {len(chunks)} chunks")
    finally:
        await conn.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def ingest(agreement_filter: str | None) -> None:
    kb = _load_knowledge_base()

    if agreement_filter and agreement_filter != "all":
        kb = [c for c in kb if c["agreement"] == agreement_filter]

    print(f"Processing {len(kb)} knowledge base entries...")

    # Build flat list of (meta, text) to embed
    records: list[dict] = []
    for entry in kb:
        sub_chunks = chunk_text(entry["content"])
        for sc in sub_chunks:
            records.append({"agreement": entry["agreement"], "source": entry["source"], "content": sc})

    print(f"  → {len(records)} chunks after splitting")

    # Batch embed (Voyage rate limit: 128 texts / request)
    BATCH = 64
    all_embeddings: list[list[float]] = []
    for i in range(0, len(records), BATCH):
        batch_texts = [r["content"] for r in records[i : i + BATCH]]
        print(f"  Embedding batch {i // BATCH + 1}/{(len(records) - 1) // BATCH + 1}...")
        embeddings = await embed_texts(batch_texts)
        all_embeddings.extend(embeddings)

    for rec, emb in zip(records, all_embeddings):
        rec["embedding"] = emb

    await upsert_chunks(records)
    print("Ingestion complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest FTA texts into pgvector")
    parser.add_argument("--agreement", default="all", choices=["all", "cusma", "ceta", "cptpp", "general"])
    args = parser.parse_args()
    asyncio.run(ingest(args.agreement if args.agreement != "all" else None))


if __name__ == "__main__":
    main()

"""Integration token storage and refresh helpers."""
from __future__ import annotations

import json
import time
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


# Tokens are stored in a simple kv table: integration_tokens(org_id, provider, data JSON)
# This avoids adding a new model — in production replace with an encrypted secrets store.

async def _ensure_table(db: AsyncSession) -> None:
    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS integration_tokens (
            org_id   TEXT NOT NULL,
            provider TEXT NOT NULL,
            data     JSONB NOT NULL,
            PRIMARY KEY (org_id, provider)
        )
    """))
    await db.commit()


async def save_qbo_tokens(db: AsyncSession, org_id: str, tokens: dict[str, Any]) -> None:
    await _ensure_table(db)
    tokens["stored_at"] = int(time.time())
    await db.execute(
        text("""
            INSERT INTO integration_tokens (org_id, provider, data)
            VALUES (:org_id, 'quickbooks', :data::jsonb)
            ON CONFLICT (org_id, provider) DO UPDATE SET data = EXCLUDED.data
        """),
        {"org_id": org_id, "data": json.dumps(tokens)},
    )
    await db.commit()


async def get_qbo_connection(db: AsyncSession, org_id: str) -> dict[str, Any] | None:
    try:
        await _ensure_table(db)
        result = await db.execute(
            text("SELECT data FROM integration_tokens WHERE org_id = :org_id AND provider = 'quickbooks'"),
            {"org_id": org_id},
        )
        row = result.fetchone()
        return row[0] if row else None
    except Exception:
        return None


async def remove_qbo_connection(db: AsyncSession, org_id: str) -> None:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages/integrations"))
    try:
        from quickbooks.oauth import revoke_token
        conn = await get_qbo_connection(db, org_id)
        if conn and conn.get("refresh_token"):
            await revoke_token(conn["refresh_token"])
    except Exception:
        pass  # best-effort revoke

    await db.execute(
        text("DELETE FROM integration_tokens WHERE org_id = :org_id AND provider = 'quickbooks'"),
        {"org_id": org_id},
    )
    await db.commit()


async def maybe_refresh_qbo_token(
    db: AsyncSession, org_id: str, conn: dict[str, Any]
) -> str:
    """Return a valid access token, refreshing if within 5 min of expiry."""
    stored_at = conn.get("stored_at", 0)
    expires_in = conn.get("expires_in", 3600)
    age = int(time.time()) - stored_at

    if age < expires_in - 300:
        return conn["access_token"]

    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages/integrations"))
    from quickbooks.oauth import refresh_token

    new_tokens = await refresh_token(conn["refresh_token"])
    merged = {**conn, **new_tokens, "stored_at": int(time.time())}
    await save_qbo_tokens(db, org_id, merged)
    return merged["access_token"]

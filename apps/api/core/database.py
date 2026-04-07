from collections.abc import AsyncGenerator
from typing import AsyncIterator

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core.config import get_settings

settings = get_settings()

# asyncpg requires ssl=require not sslmode=require — normalise the URL
_db_url = settings.database_url.replace("?sslmode=require", "?ssl=require").replace(
    "&sslmode=require", "&ssl=require"
)

engine = create_async_engine(
    _db_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo=not settings.is_production,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db(request: Request = None) -> AsyncGenerator[AsyncSession, None]:
    """
    Yield a DB session scoped to the current request.
    If the request carries an org_id (set by Clerk auth middleware),
    SET LOCAL app.current_org_id so PostgreSQL RLS policies can enforce
    row-level isolation at the database layer.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Set RLS context variable if org_id is available on request state
            org_id = None
            if request is not None:
                try:
                    org_id = getattr(request.state, "org_id", None)
                except Exception:
                    pass

            if org_id:
                await session.execute(
                    text("SELECT set_config('app.current_org_id', :org_id, true)"),
                    {"org_id": str(org_id)},
                )

            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

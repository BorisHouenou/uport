import ssl
from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core.config import get_settings

settings = get_settings()

# Strip SSL query params — we pass SSL via connect_args instead.
# asyncpg doesn't reliably pick up ssl/sslmode from the URL when used
# through SQLAlchemy; connect_args is the guaranteed path.
_db_url = settings.database_url
_needs_ssl = "ssl=require" in _db_url or "sslmode=require" in _db_url
for _param in ("?ssl=require", "&ssl=require", "?ssl=disable", "&ssl=disable",
               "?sslmode=require", "&sslmode=require"):
    _db_url = _db_url.replace(_param, "")

if _needs_ssl:
    # Railway PostgreSQL requires SSL. Use CERT_NONE since Railway uses
    # a self-signed cert on the internal network.
    _ssl_ctx: ssl.SSLContext | bool = ssl.create_default_context()
    _ssl_ctx.check_hostname = False  # type: ignore[union-attr]
    _ssl_ctx.verify_mode = ssl.CERT_NONE  # type: ignore[union-attr]
else:
    _ssl_ctx = False  # local development — no SSL

engine = create_async_engine(
    _db_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo=not settings.is_production,
    pool_pre_ping=True,
    connect_args={"ssl": _ssl_ctx},
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

"""Clerk webhook event handler — provisions users and orgs in the DB."""

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from models.organization import Organization
from models.user import User

logger = structlog.get_logger()


async def handle_clerk_event(payload: dict) -> None:
    event_type = payload.get("type", "")
    data = payload.get("data", {})

    async with AsyncSessionLocal() as session:
        try:
            if event_type == "organization.created":
                await _upsert_organization(session, data)
            elif event_type == "organization.updated":
                await _upsert_organization(session, data)
            elif event_type == "organization.deleted":
                await _delete_organization(session, data)
            elif event_type == "user.created":
                await _upsert_user(session, data)
            elif event_type == "user.updated":
                await _upsert_user(session, data)
            else:
                logger.info("clerk_event_ignored", event_type=event_type)
                return

            await session.commit()
            logger.info("clerk_event_handled", event_type=event_type)
        except Exception as exc:
            await session.rollback()
            logger.error("clerk_event_failed", event_type=event_type, error=str(exc))
            raise


async def _upsert_organization(session: AsyncSession, data: dict) -> None:
    clerk_org_id = data.get("id")
    if not clerk_org_id:
        return

    result = await session.execute(
        select(Organization).where(Organization.clerk_org_id == clerk_org_id)
    )
    org = result.scalar_one_or_none()

    # Extract country from public_metadata, fall back to "US"
    meta = data.get("public_metadata") or {}
    country = meta.get("country", "US")[:2].upper()

    if org:
        org.name = data.get("name", org.name)
        org.country = country
    else:
        org = Organization(
            clerk_org_id=clerk_org_id,
            name=data.get("name", "Unnamed Organization"),
            country=country,
            plan="starter",
            subscription_tier="starter",
            subscription_status="none",
        )
        session.add(org)


async def _delete_organization(session: AsyncSession, data: dict) -> None:
    clerk_org_id = data.get("id")
    if not clerk_org_id:
        return
    result = await session.execute(
        select(Organization).where(Organization.clerk_org_id == clerk_org_id)
    )
    org = result.scalar_one_or_none()
    if org:
        org.is_active = False


async def _upsert_user(session: AsyncSession, data: dict) -> None:
    clerk_user_id = data.get("id")
    if not clerk_user_id:
        return

    # Clerk puts org memberships in organization_memberships[]
    memberships = data.get("organization_memberships") or []
    clerk_org_id = (
        memberships[0].get("organization", {}).get("id") if memberships else None
    )

    # Resolve internal org — create a personal org if none
    org = None
    if clerk_org_id:
        result = await session.execute(
            select(Organization).where(Organization.clerk_org_id == clerk_org_id)
        )
        org = result.scalar_one_or_none()

    if not org:
        # Personal workspace: provision a stub org keyed on the user id
        personal_org_id = f"personal_{clerk_user_id}"
        result = await session.execute(
            select(Organization).where(Organization.clerk_org_id == personal_org_id)
        )
        org = result.scalar_one_or_none()
        if not org:
            email_addresses = data.get("email_addresses") or []
            primary = next(
                (
                    e
                    for e in email_addresses
                    if e.get("id") == data.get("primary_email_address_id")
                ),
                None,
            )
            email = (primary or {}).get("email_address", "")
            org = Organization(
                clerk_org_id=personal_org_id,
                name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
                or email,
                country="US",
                plan="starter",
                subscription_tier="starter",
                subscription_status="none",
            )
            session.add(org)
            await session.flush()

    email_addresses = data.get("email_addresses") or []
    primary = next(
        (
            e
            for e in email_addresses
            if e.get("id") == data.get("primary_email_address_id")
        ),
        None,
    )
    email = (primary or {}).get("email_address", "")

    result = await session.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    user = result.scalar_one_or_none()

    if user:
        user.email = email or user.email
        user.first_name = data.get("first_name")
        user.last_name = data.get("last_name")
        user.org_id = org.id
    else:
        user = User(
            clerk_user_id=clerk_user_id,
            org_id=org.id,
            email=email,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            role="admin",
        )
        session.add(user)

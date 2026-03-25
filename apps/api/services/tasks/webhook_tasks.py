"""Celery tasks for outbound webhook delivery."""
import asyncio
import uuid
from datetime import date

import structlog
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(name="webhook_tasks.fire_expired_declarations", bind=True, max_retries=0)
def fire_expired_declarations(self):
    """
    Daily beat task: fire declaration.expired webhooks for declarations
    that expired today (valid_until == yesterday or earlier, not yet notified).
    """
    from sqlalchemy import create_engine
    from core.config import get_settings
    from models.supplier import SupplierDeclaration
    from services.webhook_delivery_service import fire_event_sync

    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    today = date.today()

    with Session(engine) as session:
        # Find declarations that expired in the last 24 h
        expired = session.execute(
            select(SupplierDeclaration).where(
                SupplierDeclaration.valid_until < today,
                SupplierDeclaration.notified_expired.is_(False),
            )
        ).scalars().all()

        for decl in expired:
            try:
                asyncio.run(fire_event_sync(
                    org_id=uuid.UUID(str(decl.org_id)),
                    event_type="declaration.expired",
                    payload={
                        "declaration_id": str(decl.id),
                        "supplier_name": decl.supplier_name,
                        "product_id": str(decl.product_id),
                        "valid_until": str(decl.valid_until),
                    },
                ))
                # Mark as notified to avoid duplicate firings
                decl.notified_expired = True
            except Exception as exc:
                logger.warning("expired_webhook_error", declaration_id=str(decl.id), error=str(exc))

        session.commit()
    logger.info("expired_declarations_checked", count=len(expired))

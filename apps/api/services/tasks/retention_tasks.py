"""Data retention enforcement — PIPEDA 7-year / GDPR 3-year audit log purge."""
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import delete
from sqlalchemy.orm import Session

from core.celery_app import celery_app

logger = structlog.get_logger()

# Audit events older than this are hard-deleted (configurable via env)
AUDIT_RETENTION_DAYS = 7 * 365   # 7 years default (Canadian customs requirement)
CHAT_RETENTION_DAYS  = 2 * 365   # 2 years for chat messages


@celery_app.task(name="retention_tasks.enforce_retention", bind=True, max_retries=0)
def enforce_retention(self):
    """
    Weekly beat task: hard-delete audit_events and chat_messages
    older than the configured retention period.
    """
    from sqlalchemy import create_engine, text
    from core.config import get_settings
    from models.audit import AuditEvent

    settings = get_settings()
    engine = create_engine(settings.database_url_sync)

    audit_cutoff = datetime.now(timezone.utc) - timedelta(days=AUDIT_RETENTION_DAYS)
    chat_cutoff  = datetime.now(timezone.utc) - timedelta(days=CHAT_RETENTION_DAYS)

    with Session(engine) as session:
        # Hard-delete old audit events
        result = session.execute(
            delete(AuditEvent).where(AuditEvent.created_at < audit_cutoff)
        )
        audit_deleted = result.rowcount

        # Hard-delete old chat messages (raw SQL — ChatMessage model in separate migration)
        result2 = session.execute(
            text("DELETE FROM chat_messages WHERE created_at < :cutoff"),
            {"cutoff": chat_cutoff},
        )
        chat_deleted = result2.rowcount

        session.commit()

    logger.info(
        "retention_enforced",
        audit_deleted=audit_deleted,
        chat_deleted=chat_deleted,
        audit_cutoff=audit_cutoff.isoformat(),
    )

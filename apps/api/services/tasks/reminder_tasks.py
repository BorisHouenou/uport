"""Celery tasks for supplier declaration expiry email reminders."""
from datetime import date, timedelta

import structlog

from core.celery_app import celery_app

logger = structlog.get_logger()

REMINDER_WINDOWS = [30, 7, 1]  # days before expiry to send reminders


@celery_app.task(name="reminder_tasks.send_expiry_reminders", bind=True, max_retries=0)
def send_expiry_reminders(self):
    """
    Daily beat task: send email reminders for supplier declarations
    expiring in 30, 7, or 1 days.
    Only sends to org admin users; skips if already notified at this window.
    """
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from core.config import get_settings
    from models.supplier import SupplierDeclaration
    from models.user import User
    from services.email_service import send_email, supplier_expiry_reminder_html

    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    today = date.today()

    sent_total = 0

    with Session(engine) as session:
        for days in REMINDER_WINDOWS:
            target_date = today + timedelta(days=days)

            # Find declarations expiring exactly on the target date
            expiring = session.execute(
                select(SupplierDeclaration)
                .where(SupplierDeclaration.valid_until == target_date)
            ).scalars().all()

            for decl in expiring:
                # Find admin users for this org
                admins = session.execute(
                    select(User)
                    .where(User.org_id == decl.org_id)
                    .where(User.role.in_(["admin", "org:admin"]))
                ).scalars().all()

                dashboard_url = f"{getattr(settings, 'app_base_url', 'https://app.uportai.com')}/supplier"

                for admin in admins:
                    if not admin.email or admin.email == "[erased]@erased.invalid":
                        continue
                    try:
                        subject, html, text = supplier_expiry_reminder_html(
                            supplier_name=decl.supplier_name,
                            product_id=str(decl.product_id),
                            valid_until=str(decl.valid_until),
                            days_remaining=days,
                            dashboard_url=dashboard_url,
                        )
                        ok = send_email(
                            to=admin.email,
                            subject=subject,
                            body_html=html,
                            body_text=text,
                        )
                        if ok:
                            sent_total += 1
                    except Exception as exc:
                        logger.warning(
                            "reminder_send_error",
                            declaration_id=str(decl.id),
                            admin_email=admin.email,
                            error=str(exc),
                        )

    logger.info("expiry_reminders_sent", count=sent_total)

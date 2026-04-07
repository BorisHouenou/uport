import ssl

from celery import Celery

from core.config import get_settings

settings = get_settings()

# Upstash Redis uses rediss:// (TLS) — Celery needs explicit SSL options
_ssl_opts: dict = {}
if settings.celery_broker_url.startswith("rediss://"):
    _ssl_opts = {
        "broker_use_ssl": {"ssl_cert_reqs": ssl.CERT_NONE},
        "redis_backend_use_ssl": {"ssl_cert_reqs": ssl.CERT_NONE},
    }

celery_app = Celery(
    "uportai",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "services.tasks.bom_tasks",
        "services.tasks.certificate_tasks",
        "services.tasks.ai_tasks",
        "services.tasks.webhook_tasks",
        "services.tasks.retention_tasks",
        "services.tasks.reminder_tasks",
        "services.tasks.finetuning_tasks",
    ],
)

celery_app.conf.update(
    **_ssl_opts,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
    beat_schedule={
        "check-expired-declarations-daily": {
            "task": "webhook_tasks.fire_expired_declarations",
            "schedule": 86400,  # every 24 hours
        },
        "enforce-data-retention-weekly": {
            "task": "retention_tasks.enforce_retention",
            "schedule": 7 * 86400,  # every 7 days
        },
        "send-expiry-reminders-daily": {
            "task": "reminder_tasks.send_expiry_reminders",
            "schedule": 86400,  # every 24 hours
        },
        "export-finetuning-corrections-weekly": {
            "task": "finetuning_tasks.export_corrections",
            "schedule": 7 * 86400,  # every 7 days
        },
    },
)

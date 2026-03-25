"""Certificate generation Celery task."""
import os
import sys

from core.celery_app import celery_app


@celery_app.task(name="certs.generate", bind=True, max_retries=3)
def generate_certificate_task(self, org_id: str, shipment_id: str, cert_type: str, determination_id: str):
    """Generate and store a Certificate of Origin PDF."""
    try:
        from services.certificate_service import generate_and_store_certificate_sync
        result = generate_and_store_certificate_sync(org_id, shipment_id, cert_type, determination_id)
        return {"status": "completed", "certificate_id": result["certificate_id"], "pdf_url": result["pdf_url"]}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)

"""Certificate generation task stubs — implemented in Sprint 5–6."""
from core.celery_app import celery_app


@celery_app.task(name="certs.generate", bind=True, max_retries=3)
def generate_certificate_task(self, org_id: str, shipment_id: str, cert_type: str, determination_id: str):
    """Generate and store a Certificate of Origin PDF."""
    raise NotImplementedError("Implemented in Sprint 5–6")

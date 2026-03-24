"""BOM processing task stubs — implemented in Sprint 3–4."""
from core.celery_app import celery_app


@celery_app.task(name="bom.process_upload", bind=True, max_retries=3)
def process_bom_upload(self, org_id: str, product_id: str, file_content: str, file_ext: str):
    """Parse a BOM file and classify each line item via HS classifier agent."""
    raise NotImplementedError("Implemented in Sprint 3–4")

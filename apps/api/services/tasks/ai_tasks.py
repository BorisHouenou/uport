"""Async AI task stubs — implemented in Sprint 3–4."""
from core.celery_app import celery_app


@celery_app.task(name="ai.run_origin_determination", bind=True, max_retries=3)
def run_origin_determination(self, org_id: str, shipment_id: str, agreement_codes: list[str]):
    """Run origin determination agents for the given shipment."""
    raise NotImplementedError("Implemented in Sprint 3–4")


@celery_app.task(name="ai.classify_hs_code", bind=True, max_retries=3)
def classify_hs_code_task(self, description: str, org_id: str):
    """AI-powered HS code classification."""
    raise NotImplementedError("Implemented in Sprint 3–4")

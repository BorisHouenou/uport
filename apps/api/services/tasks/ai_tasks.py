"""
AI Celery tasks — Sprint 3-4 implementation.
Bridges the API layer to the AI agent packages.
"""
import json
import os
import sys

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'packages', 'ai-agents'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'packages', 'roo-engine'))

from core.celery_app import celery_app


@celery_app.task(name="ai.run_origin_determination", bind=True, max_retries=3)
def run_origin_determination(self, org_id: str, shipment_id: str, agreement_codes: list):
    """Run the full origin determination workflow for a shipment."""
    try:
        from origin_agent import ShipmentInput, run_origin_determination as _run
        from services.origin_service import get_shipment_data_sync, save_determination_sync

        # Fetch shipment data from DB (sync version for Celery)
        shipment_data = get_shipment_data_sync(shipment_id, org_id)
        if not shipment_data:
            raise ValueError(f"Shipment {shipment_id} not found")

        shipment_input = ShipmentInput(
            hs_code=shipment_data["hs_code"],
            product_description=shipment_data["product_description"],
            production_country=shipment_data["origin_country"],
            destination_country=shipment_data["destination_country"],
            transaction_value_usd=shipment_data["shipment_value_usd"] or 0.0,
            bom=shipment_data.get("bom", []),
            agreement_codes=agreement_codes or [],
        )

        result = _run(shipment_input, shipment_id=shipment_id)
        save_determination_sync(shipment_id, org_id, result)
        return {"status": "completed", "best_agreement": result.best_agreement}

    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(name="ai.classify_hs_code", bind=True, max_retries=2)
def classify_hs_code_task(self, description: str, org_id: str):
    """Classify a product description to an HS code."""
    try:
        from hs_classifier import classify
        result = classify(description)
        return {
            "hs_code": result.hs_code,
            "description": result.hs_description,
            "confidence": result.confidence,
            "alternatives": [a.model_dump() for a in result.alternatives],
            "reasoning": result.reasoning,
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=15)

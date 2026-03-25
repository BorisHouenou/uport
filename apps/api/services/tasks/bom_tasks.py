"""BOM processing Celery task — Sprint 3-4 implementation."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'packages', 'ai-agents'))

from core.celery_app import celery_app


@celery_app.task(name="bom.process_upload", bind=True, max_retries=3)
def process_bom_upload(self, org_id: str, product_id: str, file_content: str, file_ext: str):
    """
    Parse a BOM file, classify each line item's HS code, and persist to DB.
    file_content is hex-encoded bytes.
    """
    try:
        from bom_parser import parse_bom
        from hs_classifier import classify
        from services.bom_service import save_bom_items_sync

        content = bytes.fromhex(file_content)
        rows = parse_bom(content, file_ext)

        bom_items = []
        for row in rows:
            hs_code = row.hs_code
            hs_confidence = None

            # Classify if no HS code provided
            if not hs_code and row.description:
                result = classify(row.description)
                if result.confidence >= 0.5:
                    hs_code = result.hs_code
                    hs_confidence = result.confidence

            bom_items.append({
                "product_id": product_id,
                "description": row.description,
                "quantity": row.quantity,
                "unit_cost": row.unit_cost,
                "currency": row.currency,
                "origin_country": row.origin_country,
                "hs_code": hs_code,
                "hs_confidence": hs_confidence,
                "is_originating": row.is_originating,
                "classified_by": "ai" if hs_confidence else ("imported" if row.hs_code else "manual"),
            })

        save_bom_items_sync(product_id, org_id, bom_items)
        return {"status": "completed", "items_processed": len(bom_items)}

    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(name="bom.process_from_rows", bind=True, max_retries=3)
def process_bom_from_rows(self, product_id: str, rows: list[dict], org_id: str):
    """
    Classify and persist BOM rows that were already parsed (e.g. imported from QBO).
    rows: list of dicts matching BOMRow shape.
    """
    try:
        from hs_classifier import classify
        from services.bom_service import save_bom_items_sync

        bom_items = []
        for row in rows:
            hs_code = row.get("hs_code")
            hs_confidence = None

            if not hs_code and row.get("description"):
                result = classify(row["description"])
                if result.confidence >= 0.5:
                    hs_code = result.hs_code
                    hs_confidence = result.confidence

            bom_items.append({
                "product_id": product_id,
                "description": row.get("description", ""),
                "quantity": row.get("quantity", 1.0),
                "unit_cost": row.get("unit_cost", 0.0),
                "currency": row.get("currency", "USD"),
                "origin_country": row.get("origin_country"),
                "hs_code": hs_code,
                "hs_confidence": hs_confidence,
                "is_originating": row.get("is_originating"),
                "classified_by": "ai" if hs_confidence else "imported",
            })

        save_bom_items_sync(product_id, org_id, bom_items)
        return {"status": "completed", "items_processed": len(bom_items)}

    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)

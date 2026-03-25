"""
Fine-tuning data export task.

Weekly beat task: exports all un-exported human corrections as a JSONL
fine-tuning dataset to S3 at:
  s3://{bucket}/fine-tuning/{YYYY-MM-DD}/corrections.jsonl

Format (Anthropic Messages API fine-tuning format):
  {"messages": [
      {"role": "user",      "content": "<product description + rule context>"},
      {"role": "assistant", "content": "<corrected result JSON>"}
  ]}
"""
import json
from datetime import datetime, timezone

import structlog

from core.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(name="finetuning_tasks.export_corrections", bind=True, max_retries=0)
def export_corrections(self):
    """Export pending human corrections as JSONL fine-tuning dataset to S3."""
    from sqlalchemy import create_engine, select, update
    from sqlalchemy.orm import Session
    from core.config import get_settings
    from models.correction import HumanCorrection

    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    today = datetime.now(timezone.utc).date().isoformat()

    with Session(engine) as session:
        # Fetch corrections not yet exported
        corrections = session.execute(
            select(HumanCorrection).where(HumanCorrection.exported_at.is_(None))
        ).scalars().all()

        if not corrections:
            logger.info("finetuning_export_skipped", reason="no new corrections")
            return

        # Build JSONL
        lines = []
        for c in corrections:
            user_content = _build_user_prompt(c)
            assistant_content = json.dumps({
                "result": c.corrected_result or c.original_result,
                "rule_applied": c.corrected_rule or c.original_rule,
                "agreement_code": c.agreement_code,
                "reviewer_notes": c.reviewer_notes,
            })
            lines.append(json.dumps({
                "messages": [
                    {"role": "user",      "content": user_content},
                    {"role": "assistant", "content": assistant_content},
                ]
            }))

        jsonl_content = "\n".join(lines).encode("utf-8")
        s3_key = f"fine-tuning/{today}/corrections.jsonl"

        # Upload to S3
        try:
            import boto3
            s3 = boto3.client("s3", region_name=settings.aws_region)
            s3.put_object(
                Bucket=settings.s3_bucket_documents,
                Key=s3_key,
                Body=jsonl_content,
                ContentType="application/jsonl",
            )
            logger.info("finetuning_exported", count=len(corrections), s3_key=s3_key)
        except Exception as exc:
            logger.error("finetuning_s3_upload_failed", error=str(exc))
            return  # Don't mark as exported if upload failed

        # Mark corrections as exported
        ids = [c.id for c in corrections]
        session.execute(
            update(HumanCorrection)
            .where(HumanCorrection.id.in_(ids))
            .values(exported_at=datetime.now(timezone.utc))
        )
        session.commit()


def _build_user_prompt(c: HumanCorrection) -> str:
    parts = [
        "You are an expert in Rules of Origin compliance.",
        f"Agreement: {c.agreement_code or 'unknown'}",
        f"Original determination: {c.original_result or 'unknown'}",
        f"Original rule applied: {c.original_rule or 'unknown'}",
    ]
    if c.product_description:
        parts.append(f"Product: {c.product_description}")
    parts.append("Based on the above, provide the correct origin determination.")
    return "\n".join(parts)

"""Certificate generation, storage, and retrieval service."""
from __future__ import annotations

import io
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

import boto3
import structlog
from botocore.exceptions import ClientError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from models import Certificate, OriginDetermination, Organization, Product, Shipment

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'packages', 'certificate-gen'))

logger = structlog.get_logger()
settings = get_settings()


async def get_certificate_pdf(
    db: AsyncSession,
    certificate_id: uuid.UUID,
    org_id: uuid.UUID,
) -> bytes | None:
    result = await db.execute(
        select(Certificate)
        .join(Shipment, Certificate.shipment_id == Shipment.id)
        .where(Certificate.id == certificate_id)
        .where(Shipment.org_id == org_id)
    )
    cert = result.scalar_one_or_none()
    if not cert or not cert.s3_key:
        return None
    return _download_from_s3(cert.s3_key)


async def list_org_certificates(
    db: AsyncSession,
    org_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Certificate)
        .join(Shipment, Certificate.shipment_id == Shipment.id)
        .where(Shipment.org_id == org_id)
        .order_by(Certificate.created_at.desc())
        .offset(offset).limit(page_size)
    )
    certs = result.scalars().all()
    return {"certificates": certs, "total": len(certs), "page": page, "page_size": page_size}


def _report_cert_usage_sync(org_id: str, stripe_sub_id: str | None) -> None:
    """Report one certificate unit to Stripe metered billing (sync, Celery-safe)."""
    if not stripe_sub_id:
        return
    import stripe as stripe_lib
    from services.billing_service import PRICE_CERT_OVERAGE
    if PRICE_CERT_OVERAGE == "price_cert_overage_placeholder":
        return
    stripe_lib.api_key = settings.stripe_secret_key
    try:
        sub = stripe_lib.Subscription.retrieve(stripe_sub_id, expand=["items"])
        metered_item = next(
            (item for item in sub["items"]["data"] if item["price"]["id"] == PRICE_CERT_OVERAGE),
            None,
        )
        if metered_item:
            stripe_lib.SubscriptionItem.create_usage_record(
                metered_item["id"], quantity=1, action="increment"
            )
    except Exception:
        pass


def generate_and_store_certificate_sync(
    org_id: str,
    shipment_id: str,
    cert_type: str,
    determination_id: str,
) -> dict:
    """Generate PDF and persist to DB + S3. Sync for Celery."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine(settings.database_url_sync)

    with Session(engine) as session:
        # Load all required data
        ship = session.execute(
            select(Shipment).where(Shipment.id == uuid.UUID(shipment_id))
        ).scalar_one()
        det = session.execute(
            select(OriginDetermination).where(OriginDetermination.id == uuid.UUID(determination_id))
        ).scalar_one_or_none()
        org = session.execute(
            select(Organization).where(Organization.id == uuid.UUID(org_id))
        ).scalar_one()
        product = session.execute(
            select(Product).where(Product.id == ship.product_id)
        ).scalar_one_or_none() if ship.product_id else None

        # Build CertificateData
        cert_data = _build_cert_data(ship, det, org, product, cert_type)

        # Generate PDF (with digital signature)
        from generator import generate_certificate
        pdf_bytes = generate_certificate(cert_data, sign=True)

        # Store to S3 (or local fallback)
        s3_key = f"certificates/{org_id}/{shipment_id}/{cert_data.cert_number}.pdf"
        pdf_url = _upload_to_s3(pdf_bytes, s3_key)

        # Persist Certificate record
        cert_number = cert_data.cert_number
        cert = Certificate(
            id=uuid.uuid4(),
            shipment_id=uuid.UUID(shipment_id),
            determination_id=uuid.UUID(determination_id) if determination_id else None,
            cert_type=cert_type,
            pdf_url=pdf_url,
            s3_key=s3_key,
            issued_at=datetime.now(timezone.utc),
            valid_until=datetime.now(timezone.utc) + timedelta(days=365),
            cert_number=cert_number,
            status="issued",
        )
        session.add(cert)

        # Increment org certificate counter + report Stripe usage (best-effort)
        org.certificates_used = (org.certificates_used or 0) + 1
        session.commit()

        # Report to Stripe metered billing (sync, non-blocking)
        try:
            _report_cert_usage_sync(org_id=org_id, stripe_sub_id=getattr(org, "stripe_subscription_id", None))
        except Exception:
            pass

        # Fire outbound webhook (sync wrapper — Celery-safe)
        try:
            import asyncio
            from services.webhook_delivery_service import fire_event_sync
            asyncio.run(fire_event_sync(
                org_id=uuid.UUID(org_id),
                event_type="certificate.issued",
                payload={
                    "certificate_id": str(cert.id),
                    "cert_type": cert_type,
                    "cert_number": cert_number,
                    "shipment_id": shipment_id,
                    "pdf_url": pdf_url,
                },
            ))
        except Exception:
            pass

        return {"certificate_id": str(cert.id), "pdf_url": pdf_url}


def _build_cert_data(ship, det, org, product, cert_type: str):
    from models_cert import CertificateData, ExporterInfo, ImporterInfo, GoodLine
    import random, string

    cert_number = "UP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    origin_criterion = _infer_origin_criterion(det)

    exporter = ExporterInfo(
        name=org.name,
        address="Canada",
        country="CA",
    )
    importer = ImporterInfo(
        name="Importer",
        address=ship.destination_country,
        country=ship.destination_country,
    )
    goods = []
    if product:
        goods.append(GoodLine(
            line_no=1,
            description=product.name or product.description or "Goods",
            hs_code=product.hs_code or "0000.00",
            origin_country=ship.origin_country or "CA",
            quantity=1,
            unit="shipment",
            unit_value_usd=float(ship.shipment_value_usd or 0),
            total_value_usd=float(ship.shipment_value_usd or 0),
        ))

    return CertificateData(
        cert_type=cert_type,
        cert_number=cert_number,
        agreement_code=det.agreement_code if det else cert_type,
        agreement_name=det.agreement_name if det else cert_type.upper(),
        exporter=exporter,
        importer=importer,
        goods=goods,
        origin_criterion=origin_criterion,
        rule_applied=det.rule_applied if det else "",
        rvc_pct=None,
        issued_by=org.name,
    )


def _infer_origin_criterion(det) -> str:
    if not det:
        return "B"
    rule_type = det.rule_applied or ""
    if "wholly" in rule_type.lower():
        return "A"
    if "rvc" in rule_type.lower() or "build" in rule_type.lower():
        return "B"
    if "tariff" in rule_type.lower() or "shift" in rule_type.lower():
        return "D"
    return "B"


def _upload_to_s3(pdf_bytes: bytes, s3_key: str) -> str:
    """Upload to S3 and return a presigned URL (or local path for dev)."""
    if not settings.aws_access_key_id or settings.environment == "development":
        # Local fallback — write to /tmp
        local_path = f"/tmp/{s3_key.replace('/', '_')}"
        with open(local_path, "wb") as f:
            f.write(pdf_bytes)
        return f"file://{local_path}"

    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        s3.put_object(
            Bucket=settings.s3_bucket_documents,
            Key=s3_key,
            Body=pdf_bytes,
            ContentType="application/pdf",
            ServerSideEncryption="AES256",
        )
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket_documents, "Key": s3_key},
            ExpiresIn=86400,
        )
        return url
    except ClientError as e:
        logger.error("s3_upload_failed", key=s3_key, error=str(e))
        raise


def _download_from_s3(s3_key: str) -> bytes | None:
    if settings.environment == "development":
        local_path = f"/tmp/{s3_key.replace('/', '_')}"
        try:
            with open(local_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        obj = s3.get_object(Bucket=settings.s3_bucket_documents, Key=s3_key)
        return obj["Body"].read()
    except ClientError:
        return None

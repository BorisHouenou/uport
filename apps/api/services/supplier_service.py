"""Supplier declaration service — CRUD + S3 document attachment."""
from __future__ import annotations

import uuid
from datetime import date, timedelta

import boto3
from fastapi import UploadFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models.supplier import SupplierDeclaration
from schemas.suppliers import (
    SupplierDeclarationCreate,
    SupplierDeclarationResponse,
    SupplierDeclarationList,
)

EXPIRY_WARN_DAYS = 30


def _to_response(decl: SupplierDeclaration) -> SupplierDeclarationResponse:
    return SupplierDeclarationResponse(
        id=decl.id,
        product_id=decl.product_id,
        supplier_name=decl.supplier_name,
        supplier_country=decl.supplier_country,
        origin_country=decl.origin_country,
        valid_from=decl.valid_from,
        valid_until=decl.valid_until,
        doc_url=decl.doc_url,
        is_expired=decl.valid_until < date.today(),
        created_at=decl.created_at,
        updated_at=decl.updated_at,
    )


async def upsert_declaration(
    db: AsyncSession,
    payload: SupplierDeclarationCreate,
    org_id: str,
) -> SupplierDeclarationResponse:
    """Insert or update declaration for (org, product, supplier_name)."""
    result = await db.execute(
        select(SupplierDeclaration).where(
            SupplierDeclaration.org_id == org_id,
            SupplierDeclaration.product_id == payload.product_id,
            SupplierDeclaration.supplier_name == payload.supplier_name,
        )
    )
    decl = result.scalar_one_or_none()

    if decl is None:
        decl = SupplierDeclaration(
            org_id=org_id,
            product_id=payload.product_id,
            supplier_name=payload.supplier_name,
        )
        db.add(decl)

    decl.supplier_country = payload.supplier_country
    decl.origin_country = payload.origin_country
    decl.valid_from = payload.valid_from
    decl.valid_until = payload.valid_until
    decl.declaration_text = payload.declaration_text

    await db.commit()
    await db.refresh(decl)
    return _to_response(decl)


async def attach_document(
    db: AsyncSession,
    declaration_id: uuid.UUID,
    file: UploadFile,
    org_id: str,
) -> str:
    """Upload supporting document to S3 and persist the URL."""
    result = await db.execute(
        select(SupplierDeclaration).where(
            SupplierDeclaration.id == declaration_id,
            SupplierDeclaration.org_id == org_id,
        )
    )
    decl = result.scalar_one_or_none()
    if decl is None:
        raise ValueError("Declaration not found")

    content = await file.read()
    s3_key = f"supplier-docs/{org_id}/{declaration_id}/{file.filename}"

    if settings.environment == "development":
        import os, pathlib
        path = pathlib.Path(f"/tmp/{s3_key}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        doc_url = f"file://{path}"
    else:
        s3 = boto3.client("s3", region_name=settings.aws_region)
        s3.put_object(
            Bucket=settings.s3_bucket,
            Key=s3_key,
            Body=content,
            ContentType=file.content_type or "application/octet-stream",
        )
        doc_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket, "Key": s3_key},
            ExpiresIn=86400,
        )

    decl.doc_url = doc_url
    decl.s3_key = s3_key
    await db.commit()
    return doc_url


async def list_declarations(
    db: AsyncSession,
    org_id: str,
    expiring_within_days: int | None,
) -> SupplierDeclarationList:
    stmt = select(SupplierDeclaration).where(SupplierDeclaration.org_id == org_id)
    if expiring_within_days is not None:
        cutoff = date.today() + timedelta(days=expiring_within_days)
        stmt = stmt.where(SupplierDeclaration.valid_until <= cutoff)

    result = await db.execute(stmt.order_by(SupplierDeclaration.valid_until))
    declarations = result.scalars().all()

    warn_cutoff = date.today() + timedelta(days=EXPIRY_WARN_DAYS)
    expiring_soon = sum(1 for d in declarations if date.today() <= d.valid_until <= warn_cutoff)

    return SupplierDeclarationList(
        declarations=[_to_response(d) for d in declarations],
        total=len(declarations),
        expiring_soon=expiring_soon,
    )


async def get_declaration_by_id(
    db: AsyncSession,
    declaration_id: uuid.UUID,
    org_id: str,
) -> SupplierDeclarationResponse | None:
    result = await db.execute(
        select(SupplierDeclaration).where(
            SupplierDeclaration.id == declaration_id,
            SupplierDeclaration.org_id == org_id,
        )
    )
    decl = result.scalar_one_or_none()
    return _to_response(decl) if decl else None

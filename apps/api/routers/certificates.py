"""Certificate of origin generation and management."""
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from schemas.certificates import CertificateCreate, CertificateResponse, CertificateListResponse

router = APIRouter(prefix="/certificates", tags=["certificates"])
_limiter = Limiter(key_func=get_remote_address)

CertificateType = Literal["cusma", "eur1", "form_a", "generic"]


@router.post("/generate", response_model=CertificateResponse, status_code=201)
@_limiter.limit("20/minute")
async def generate_certificate(
    request: Request,
    payload: CertificateCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a Certificate of Origin for a shipment.
    Requires a completed origin determination. Returns PDF URL + structured data.
    """
    from services.tasks.certificate_tasks import generate_certificate_task
    task = generate_certificate_task.delay(
        org_id=current_user["org_id"],
        shipment_id=str(payload.shipment_id),
        cert_type=payload.cert_type,
        determination_id=str(payload.determination_id),
    )
    return CertificateResponse(
        task_id=task.id,
        status="generating",
        shipment_id=payload.shipment_id,
        cert_type=payload.cert_type,
    )


@router.get("/{certificate_id}/download")
async def download_certificate(
    certificate_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Stream the PDF certificate for download."""
    from services.certificate_service import get_certificate_pdf
    pdf_bytes = await get_certificate_pdf(db, certificate_id, current_user["org_id"])
    if not pdf_bytes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=certificate_{certificate_id}.pdf"},
    )


@router.get("/", response_model=CertificateListResponse)
async def list_certificates(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
):
    """List all certificates for the organization."""
    from services.certificate_service import list_org_certificates
    return await list_org_certificates(db, current_user["org_id"], page, page_size)

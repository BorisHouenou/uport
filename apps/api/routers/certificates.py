"""Certificate of origin generation and management."""
import io
import random
import string
import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from models import Certificate, OriginDetermination, Organization, Shipment
from schemas.certificates import CertificateCreate, CertificateListResponse, CertificateResponse

router = APIRouter(prefix="/certificates", tags=["certificates"])
_limiter = Limiter(key_func=get_remote_address)

CertificateType = Literal["cusma", "eur1", "form_a", "generic"]


def _generate_cert_number() -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"UP-{suffix}"


def _build_pdf(cert_number: str, cert_type: str, org_name: str, shipment, determination, product) -> bytes:
    """Generate a Certificate of Origin PDF using reportlab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("T", parent=styles["Heading1"], fontSize=16, spaceAfter=4, alignment=1)
    sub_style = ParagraphStyle("S", parent=styles["Normal"], fontSize=10, spaceAfter=12, alignment=1,
                               textColor=colors.HexColor("#555555"))
    label_style = ParagraphStyle("L", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#777777"))
    value_style = ParagraphStyle("V", parent=styles["Normal"], fontSize=10, spaceAfter=4)

    _NAMES = {
        "cusma": "Canada-United States-Mexico Agreement (CUSMA/USMCA)",
        "ceta": "Canada-EU Comprehensive Economic and Trade Agreement (CETA)",
        "cptpp": "Comprehensive and Progressive Agreement for Trans-Pacific Partnership (CPTPP)",
        "ckfta": "Canada-Korea Free Trade Agreement (CKFTA)",
        "generic": "Certificate of Origin",
    }
    agreement_name = _NAMES.get(cert_type, cert_type.upper())

    origin_criterion = "B"
    if determination:
        rule = (determination.rule_applied or "").lower()
        if "wholly" in rule:
            origin_criterion = "A"
        elif "tariff" in rule or "shift" in rule:
            origin_criterion = "D"

    product_name = product.name if product else "Goods"
    hs_code = (product.hs_code if product else None) or "0000.00"
    rvc_text = (determination.rule_text or "") if determination else ""

    story = []
    story.append(Paragraph("CERTIFICATE OF ORIGIN", title_style))
    story.append(Paragraph(agreement_name, sub_style))

    now = datetime.now(timezone.utc)
    meta = [
        ["Certificate No.", cert_number, "Date of Issue", now.strftime("%Y-%m-%d")],
        ["Valid Until", (now + timedelta(days=365)).strftime("%Y-%m-%d"), "Origin Criterion", origin_criterion],
    ]
    mt = Table(meta, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,-1), colors.HexColor("#f0f0f0")),
        ("BACKGROUND", (2,0),(2,-1), colors.HexColor("#f0f0f0")),
        ("FONTNAME", (0,0),(-1,-1), "Helvetica"),
        ("FONTNAME", (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0),(2,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0),(-1,-1), 9),
        ("BOX", (0,0),(-1,-1), 0.5, colors.black),
        ("INNERGRID", (0,0),(-1,-1), 0.25, colors.grey),
        ("PADDING", (0,0),(-1,-1), 6),
        ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(mt)
    story.append(Spacer(1, 12))

    parties = [
        [Paragraph("<b>EXPORTER / PRODUCER</b>", label_style), Paragraph("<b>IMPORTER / CONSIGNEE</b>", label_style)],
        [Paragraph(f"{org_name}<br/>Canada", value_style),
         Paragraph(f"Importer<br/>{shipment.destination_country}", value_style)],
    ]
    pt = Table(parties, colWidths=[3.75*inch, 3.75*inch])
    pt.setStyle(TableStyle([
        ("BOX", (0,0),(-1,-1), 0.5, colors.black),
        ("INNERGRID", (0,0),(-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#f0f0f0")),
        ("PADDING", (0,0),(-1,-1), 6),
        ("VALIGN", (0,0),(-1,-1), "TOP"),
    ]))
    story.append(pt)
    story.append(Spacer(1, 12))

    goods_header = ["#", "Description of Goods", "HS Code", "Origin", "Value (USD)", "Criterion"]
    goods_rows = [["1", product_name, hs_code, shipment.origin_country or "CA",
                   f"${float(shipment.shipment_value_usd or 0):,.2f}", origin_criterion]]
    gt = Table([goods_header] + goods_rows,
               colWidths=[0.3*inch, 2.5*inch, 0.9*inch, 0.9*inch, 1.1*inch, 0.8*inch])
    gt.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#1a365d")),
        ("TEXTCOLOR", (0,0),(-1,0), colors.white),
        ("FONTNAME", (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0),(-1,-1), 8),
        ("BOX", (0,0),(-1,-1), 0.5, colors.black),
        ("INNERGRID", (0,0),(-1,-1), 0.25, colors.grey),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [colors.white, colors.HexColor("#f9f9f9")]),
        ("PADDING", (0,0),(-1,-1), 5),
        ("ALIGN", (0,0),(-1,-1), "CENTER"),
        ("ALIGN", (1,0),(1,-1), "LEFT"),
    ]))
    story.append(gt)
    story.append(Spacer(1, 12))

    if determination:
        det_data = [
            [Paragraph("<b>RULE OF ORIGIN DETAILS</b>", label_style), ""],
            ["Rule Applied", determination.rule_applied or "N/A"],
            ["Rule Text", rvc_text or "N/A"],
            ["Result", (determination.result or "N/A").upper()],
            ["Confidence", f"{float(determination.confidence or 0)*100:.0f}%"],
        ]
        dt = Table(det_data, colWidths=[1.5*inch, 6.0*inch])
        dt.setStyle(TableStyle([
            ("SPAN", (0,0),(-1,0)),
            ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#f0f0f0")),
            ("FONTNAME", (0,1),(0,-1), "Helvetica-Bold"),
            ("FONTNAME", (1,1),(1,-1), "Helvetica"),
            ("FONTSIZE", (0,0),(-1,-1), 8),
            ("BOX", (0,0),(-1,-1), 0.5, colors.black),
            ("INNERGRID", (0,0),(-1,-1), 0.25, colors.grey),
            ("PADDING", (0,0),(-1,-1), 5),
            ("VALIGN", (0,0),(-1,-1), "TOP"),
        ]))
        story.append(dt)
        story.append(Spacer(1, 12))

    decl = (
        f"I, the undersigned, hereby declare that the goods described above originate in Canada "
        f"and that the information provided in this certificate is true and correct. "
        f"These goods qualify for preferential tariff treatment under {agreement_name}."
    )
    story.append(Paragraph("<b>CERTIFICATION</b>", label_style))
    story.append(Paragraph(decl, value_style))
    story.append(Spacer(1, 24))

    sig_data = [
        ["Authorized Signature", "Name & Title", "Date"],
        ["\n\n________________________", org_name, now.strftime("%Y-%m-%d")],
    ]
    st = Table(sig_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
    st.setStyle(TableStyle([
        ("FONTNAME", (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0),(-1,-1), 8),
        ("BOX", (0,0),(-1,-1), 0.5, colors.black),
        ("INNERGRID", (0,0),(-1,-1), 0.25, colors.grey),
        ("PADDING", (0,0),(-1,-1), 6),
        ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#f0f0f0")),
    ]))
    story.append(st)

    doc.build(story)
    return buf.getvalue()


# ── Routes — fixed routes MUST come before parameterized routes ────────────────

@router.get("/", response_model=CertificateListResponse)
async def list_certificates(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
):
    """List all certificates for the organization."""
    org_id = uuid.UUID(current_user["org_id"])
    offset = (page - 1) * page_size

    q = (
        select(Certificate)
        .join(Shipment, Certificate.shipment_id == Shipment.id)
        .where(Shipment.org_id == org_id)
        .order_by(Certificate.issued_at.desc())
    )
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    rows = (await db.execute(q.offset(offset).limit(page_size))).scalars().all()

    return {
        "certificates": [
            {
                "id": str(c.id),
                "shipment_id": str(c.shipment_id),
                "cert_type": c.cert_type,
                "cert_number": c.cert_number,
                "pdf_url": c.pdf_url or "",
                "issued_at": c.issued_at,
                "valid_until": c.valid_until,
                "status": c.status,
            }
            for c in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


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
    Requires a completed origin determination. Returns certificate record with download link.
    """
    org_id = uuid.UUID(current_user["org_id"])

    ship_result = await db.execute(
        select(Shipment).where(Shipment.id == payload.shipment_id, Shipment.org_id == org_id)
    )
    shipment = ship_result.scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    det_result = await db.execute(
        select(OriginDetermination).where(OriginDetermination.id == payload.determination_id)
    )
    determination = det_result.scalar_one_or_none()

    org_result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = org_result.scalar_one_or_none()
    org_name = org.name if org else "Exporter"

    product = None
    if shipment.product_id:
        from models import Product
        prod_result = await db.execute(select(Product).where(Product.id == shipment.product_id))
        product = prod_result.scalar_one_or_none()

    cert_number = _generate_cert_number()
    cert_type = payload.cert_type

    pdf_bytes = _build_pdf(cert_number, cert_type, org_name, shipment, determination, product)

    s3_key = f"certificates/{org_id}/{payload.shipment_id}/{cert_number}.pdf"
    local_path = f"/tmp/{s3_key.replace('/', '_')}"
    with open(local_path, "wb") as f:
        f.write(pdf_bytes)
    pdf_url = f"file://{local_path}"

    now = datetime.now(timezone.utc)
    cert = Certificate(
        id=uuid.uuid4(),
        shipment_id=payload.shipment_id,
        determination_id=payload.determination_id,
        cert_type=cert_type,
        pdf_url=pdf_url,
        s3_key=s3_key,
        issued_at=now,
        valid_until=now + timedelta(days=365),
        cert_number=cert_number,
        status="issued",
    )
    db.add(cert)

    if org:
        org.certificates_used = (org.certificates_used or 0) + 1

    await db.commit()
    await db.refresh(cert)

    return CertificateResponse(
        task_id=str(cert.id),
        status="completed",
        shipment_id=payload.shipment_id,
        cert_type=cert_type,
        certificate_id=cert.id,
        pdf_url=pdf_url,
        issued_at=cert.issued_at,
        valid_until=cert.valid_until,
    )


@router.get("/{certificate_id}/download")
async def download_certificate(
    certificate_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Stream the PDF certificate for download."""
    org_id = uuid.UUID(current_user["org_id"])

    result = await db.execute(
        select(Certificate)
        .join(Shipment, Certificate.shipment_id == Shipment.id)
        .where(Certificate.id == certificate_id)
        .where(Shipment.org_id == org_id)
    )
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    pdf_bytes: bytes | None = None

    if cert.s3_key:
        local_path = f"/tmp/{cert.s3_key.replace('/', '_')}"
        try:
            with open(local_path, "rb") as f:
                pdf_bytes = f.read()
        except FileNotFoundError:
            pass

    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="Certificate file not found on server — regenerate it")

    filename = f"certificate_{cert.cert_number or certificate_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

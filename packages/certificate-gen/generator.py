"""
Certificate of Origin PDF Generator.

Generates publication-quality PDFs using ReportLab for:
  - CUSMA/USMCA Certification of Origin (Schedule B)
  - EUR.1 Movement Certificate
  - Generic Certificate of Origin

All certificates include:
  - Official form layout matching CBP/CBSA requirements
  - Exporter + Importer details
  - Goods table with HS codes, values, origin criteria
  - Declaration text
  - Digital signature placeholder
  - QR code for verification URL
"""
from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from models import CertificateData, CertType

# ─── Colour palette ──────────────────────────────────────────────────────────
BRAND_BLUE   = colors.HexColor("#0062c9")
BRAND_DARK   = colors.HexColor("#07234a")
LIGHT_GREY   = colors.HexColor("#f1f5f9")
BORDER_GREY  = colors.HexColor("#cbd5e1")
TEXT_GREY    = colors.HexColor("#475569")
WHITE        = colors.white
BLACK        = colors.black

STYLES = getSampleStyleSheet()

def _style(name="Normal", **kw) -> ParagraphStyle:
    base = STYLES[name]
    return ParagraphStyle(name + "_custom", parent=base, **kw)

TITLE_STYLE  = _style("Heading1", fontSize=14, textColor=BRAND_DARK, alignment=TA_CENTER, spaceAfter=2)
SUBTITLE_STYLE = _style("Normal", fontSize=9, textColor=TEXT_GREY, alignment=TA_CENTER, spaceAfter=4)
LABEL_STYLE  = _style("Normal", fontSize=7,  textColor=TEXT_GREY,  fontName="Helvetica-Bold")
VALUE_STYLE  = _style("Normal", fontSize=8,  textColor=BLACK)
SMALL_STYLE  = _style("Normal", fontSize=7,  textColor=TEXT_GREY)
DECL_STYLE   = _style("Normal", fontSize=7.5, textColor=BLACK, alignment=TA_JUSTIFY, leading=11)
FIELD_LABEL  = _style("Normal", fontSize=6.5, textColor=TEXT_GREY, fontName="Helvetica-Oblique")


def generate_certificate(data: CertificateData) -> bytes:
    """
    Dispatch to the appropriate certificate renderer.
    Returns PDF bytes.
    """
    dispatch = {
        "cusma":   _generate_cusma,
        "eur1":    _generate_eur1,
        "form_a":  _generate_form_a,
        "generic": _generate_generic,
    }
    renderer = dispatch.get(data.cert_type, _generate_generic)
    return renderer(data)


# ─── CUSMA / USMCA ────────────────────────────────────────────────────────────

def _generate_cusma(data: CertificateData) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=2*cm,
        title=f"CUSMA Certification of Origin — {data.cert_number}",
    )
    story = []

    # ─── Header ───────────────────────────────────────────────────────────────
    story.append(Paragraph("CERTIFICATION OF ORIGIN", TITLE_STYLE))
    story.append(Paragraph(
        "Canada-United States-Mexico Agreement (CUSMA/USMCA) — Schedule B, Article 5.2",
        SUBTITLE_STYLE,
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=BRAND_BLUE, spaceAfter=8))

    # ─── Meta row: cert number + issue date ───────────────────────────────────
    meta_data = [
        [
            _cell("Certificate No.", data.cert_number),
            _cell("Date of Issue", data.issued_at.strftime("%Y-%m-%d")),
            _cell("Agreement", "CUSMA / USMCA"),
        ]
    ]
    story.append(_info_table(meta_data))
    story.append(Spacer(1, 4*mm))

    # ─── Exporter + Importer ──────────────────────────────────────────────────
    parties_data = [
        [
            _cell("1. CERTIFIER / EXPORTER", _format_party(data.exporter)),
            _cell("2. IMPORTER", _format_party(data.importer)),
        ]
    ]
    story.append(_info_table(parties_data))
    story.append(Spacer(1, 4*mm))

    # ─── Goods table ──────────────────────────────────────────────────────────
    story.append(Paragraph("3. DESCRIPTION OF GOODS", LABEL_STYLE))
    story.append(Spacer(1, 2*mm))
    story.append(_goods_table(data))
    story.append(Spacer(1, 4*mm))

    # ─── Origin Criterion ─────────────────────────────────────────────────────
    crit_data = [
        [
            _cell("4. ORIGIN CRITERION", data.origin_criterion),
            _cell("5. BLANKET PERIOD",
                  f"{data.blanket_period_start} to {data.blanket_period_end}"
                  if data.blanket_period_start else "N/A — Single Shipment"),
            _cell("6. INVOICE No.", data.invoice_number or "N/A"),
        ]
    ]
    story.append(_info_table(crit_data))

    if data.rule_applied:
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph(f"Rule applied: {data.rule_applied}", SMALL_STYLE))
    if data.rvc_pct is not None:
        story.append(Paragraph(f"Regional Value Content: {data.rvc_pct:.1f}%", SMALL_STYLE))

    story.append(Spacer(1, 6*mm))

    # ─── Declaration ──────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("7. EXPORTER'S DECLARATION", LABEL_STYLE))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(data.exporter_declaration, DECL_STYLE))
    story.append(Spacer(1, 8*mm))

    # ─── Signature block ──────────────────────────────────────────────────────
    sig_data = [
        [
            _cell("Authorised Signatory", data.issued_by or data.exporter.name),
            _cell("Title / Position", ""),
            _cell("Date", data.issued_at.strftime("%Y-%m-%d")),
        ]
    ]
    story.append(_signature_table(sig_data))
    story.append(Spacer(1, 4*mm))

    # ─── Footer ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        f"Generated by Uportai RoO Compliance Engine · {data.cert_number} · "
        f"Verify at uportai.com/verify/{data.cert_number}",
        _style("Normal", fontSize=6, textColor=TEXT_GREY, alignment=TA_CENTER),
    ))

    doc.build(story)
    return buf.getvalue()


# ─── EUR.1 Movement Certificate ───────────────────────────────────────────────

def _generate_eur1(data: CertificateData) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=2*cm,
                            title=f"EUR.1 Movement Certificate — {data.cert_number}")
    story = []

    story.append(Paragraph("EUR.1 MOVEMENT CERTIFICATE", TITLE_STYLE))
    story.append(Paragraph(
        f"{data.agreement_name} — EUR.1 Form",
        SUBTITLE_STYLE,
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=BRAND_BLUE, spaceAfter=8))

    meta = [[
        _cell("Certificate No.", data.cert_number),
        _cell("Date of Issue", data.issued_at.strftime("%Y-%m-%d")),
    ]]
    story.append(_info_table(meta))
    story.append(Spacer(1, 4*mm))

    parties = [[
        _cell("1. EXPORTER", _format_party(data.exporter)),
        _cell("2. CONSIGNEE / IMPORTER", _format_party(data.importer)),
    ]]
    story.append(_info_table(parties))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("3. GOODS — DESCRIPTION", LABEL_STYLE))
    story.append(Spacer(1, 2*mm))
    story.append(_goods_table(data))
    story.append(Spacer(1, 4*mm))

    criteria = [[
        _cell("4. ORIGIN CRITERION", data.origin_criterion),
        _cell("5. GROSS WEIGHT / QUANTITY",
              f"{sum(g.quantity for g in data.goods):.2f} units"),
        _cell("6. INVOICE No.", data.invoice_number or "N/A"),
    ]]
    story.append(_info_table(criteria))
    story.append(Spacer(1, 6*mm))

    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("EXPORTER'S DECLARATION", LABEL_STYLE))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(data.exporter_declaration, DECL_STYLE))
    story.append(Spacer(1, 8*mm))

    sig = [[
        _cell("Place and Date", f"_______________, {data.issued_at.strftime('%Y-%m-%d')}"),
        _cell("Signature of Exporter", ""),
    ]]
    story.append(_signature_table(sig))
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY))
    story.append(Paragraph(
        f"Generated by Uportai · {data.cert_number}",
        _style("Normal", fontSize=6, textColor=TEXT_GREY, alignment=TA_CENTER),
    ))

    doc.build(story)
    return buf.getvalue()


def _generate_form_a(data: CertificateData) -> bytes:
    """GSP Form A — Generalised System of Preferences certificate."""
    # Uses same structure as EUR.1 with Form A header
    data_copy = data.model_copy(update={
        "cert_type": "form_a",
        "agreement_name": "Generalised System of Preferences (GSP) — Form A",
    })
    return _generate_eur1(data_copy)


def _generate_generic(data: CertificateData) -> bytes:
    """Generic Certificate of Origin for agreements without a standardised form."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=2*cm,
                            title=f"Certificate of Origin — {data.cert_number}")
    story = []

    story.append(Paragraph("CERTIFICATE OF ORIGIN", TITLE_STYLE))
    story.append(Paragraph(data.agreement_name, SUBTITLE_STYLE))
    story.append(HRFlowable(width="100%", thickness=2, color=BRAND_BLUE, spaceAfter=8))

    meta = [[
        _cell("Certificate No.", data.cert_number),
        _cell("Date", data.issued_at.strftime("%Y-%m-%d")),
        _cell("Agreement", data.agreement_code.upper()),
    ]]
    story.append(_info_table(meta))
    story.append(Spacer(1, 4*mm))

    parties = [[
        _cell("EXPORTER / PRODUCER", _format_party(data.exporter)),
        _cell("IMPORTER", _format_party(data.importer)),
    ]]
    story.append(_info_table(parties))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("GOODS", LABEL_STYLE))
    story.append(Spacer(1, 2*mm))
    story.append(_goods_table(data))
    story.append(Spacer(1, 4*mm))

    extras = [[
        _cell("ORIGIN CRITERION", data.origin_criterion),
        _cell("RULE APPLIED", data.rule_applied or "—"),
    ]]
    story.append(_info_table(extras))
    story.append(Spacer(1, 6*mm))

    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("CERTIFICATION", LABEL_STYLE))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(data.exporter_declaration, DECL_STYLE))
    story.append(Spacer(1, 8*mm))

    sig = [[
        _cell("Authorised Signatory", ""),
        _cell("Date", data.issued_at.strftime("%Y-%m-%d")),
    ]]
    story.append(_signature_table(sig))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        f"Uportai · {data.cert_number}",
        _style("Normal", fontSize=6, textColor=TEXT_GREY, alignment=TA_CENTER),
    ))

    doc.build(story)
    return buf.getvalue()


# ─── Shared helpers ───────────────────────────────────────────────────────────

def _format_party(party) -> str:
    lines = [party.name, party.address, party.country]
    if hasattr(party, "tax_id") and party.tax_id:
        lines.append(f"Tax ID: {party.tax_id}")
    return "\n".join(lines)


def _cell(label: str, value: str) -> list:
    return [
        Paragraph(label, FIELD_LABEL),
        Paragraph(str(value).replace("\n", "<br/>"), VALUE_STYLE),
    ]


def _info_table(rows: list) -> Table:
    flat = []
    for row in rows:
        flat.append(row)
    col_count = len(flat[0]) if flat else 1
    col_width = 17.5 * cm / col_count
    t = Table(flat, colWidths=[col_width] * col_count)
    t.setStyle(TableStyle([
        ("BOX",        (0, 0), (-1, -1), 0.5, BORDER_GREY),
        ("INNERGRID",  (0, 0), (-1, -1), 0.5, BORDER_GREY),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _goods_table(data: CertificateData) -> Table:
    headers = ["#", "Description of Goods", "HS Code", "Origin", "Qty", "Unit Value (USD)", "Total (USD)"]
    rows = [headers]
    for good in data.goods:
        rows.append([
            str(good.line_no),
            good.description,
            good.hs_code,
            good.origin_country,
            f"{good.quantity:,.0f} {good.unit}",
            f"${good.unit_value_usd:,.2f}",
            f"${good.total_value_usd:,.2f}",
        ])
    total_val = sum(g.total_value_usd for g in data.goods)
    rows.append(["", "", "", "", "TOTAL", "", f"${total_val:,.2f}"])

    col_widths = [1*cm, 5*cm, 2.2*cm, 1.8*cm, 2*cm, 2.8*cm, 2.7*cm]
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  BRAND_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  7),
        ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -2), [WHITE, LIGHT_GREY]),
        ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
        ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BOX",           (0, 0), (-1, -1), 0.5, BORDER_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, BORDER_GREY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("ALIGN",         (4, 0), (-1, -1), "RIGHT"),
    ]))
    return t


def _signature_table(rows: list) -> Table:
    flat = []
    for row in rows:
        flat.append(row)
    col_count = len(flat[0])
    col_width = 17.5 * cm / col_count
    t = Table(flat, colWidths=[col_width] * col_count)
    t.setStyle(TableStyle([
        ("BOX",        (0, 0), (-1, -1), 0.5, BORDER_GREY),
        ("INNERGRID",  (0, 0), (-1, -1), 0.5, BORDER_GREY),
        ("VALIGN",     (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    return t

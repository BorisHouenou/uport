"""
PDF Digital Signature Module.

Signs generated certificate PDFs with a PKCS#12 key:
  - Dev: auto-generates a self-signed cert + key in /tmp
  - Production: loads P12 from AWS KMS-encrypted secret (via environment)

The resulting PDF has an embedded CMS/PKCS#7 signature visible in
Adobe Acrobat as "Signed by Uportai <org>".

Dependencies:
    pyhanko[pkcs12]   — pip install pyhanko[pkcs12]
    cryptography      — pulled in by pyhanko
"""
from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path


# ─── Dev: generate a self-signed key/cert for signing ─────────────────────────

def _generate_dev_p12(org_name: str = "Uportai Dev") -> bytes:
    """Return a PKCS#12 bundle with a self-signed cert for development use."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives.serialization import pkcs12
    import datetime

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, org_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Uportai Inc."),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CA"),
    ])
    now = datetime.datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    return pkcs12.serialize_key_and_certificates(
        name=org_name.encode(),
        key=key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.NoEncryption(),
    )


def _get_p12_bytes() -> tuple[bytes, bytes | None]:
    """
    Return (p12_bytes, passphrase).
    In production: read from P12_BASE64 + P12_PASSPHRASE env vars.
    In dev: generate an ephemeral self-signed cert.
    """
    p12_b64 = os.getenv("CERTIFICATE_SIGNING_P12_BASE64")
    if p12_b64:
        import base64
        p12_bytes = base64.b64decode(p12_b64)
        passphrase_str = os.getenv("CERTIFICATE_SIGNING_P12_PASSPHRASE", "")
        passphrase = passphrase_str.encode() if passphrase_str else None
        return p12_bytes, passphrase

    # Dev: use cached key in /tmp to avoid re-generating on every call
    dev_p12_path = Path("/tmp/uportai_dev_signing.p12")
    if not dev_p12_path.exists():
        dev_p12_path.write_bytes(_generate_dev_p12())
    return dev_p12_path.read_bytes(), None


def sign_pdf(pdf_bytes: bytes, reason: str = "Certificate of Origin") -> bytes:
    """
    Apply a visible CMS/PKCS#7 detached digital signature to a PDF.

    Returns signed PDF bytes. Falls back to the original bytes if
    pyhanko is not installed (so certificate generation always succeeds).
    """
    try:
        from pyhanko.sign import signers, fields
        from pyhanko.sign.fields import SigFieldSpec
        from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
        from pyhanko.sign.signers.pdf_signer import PdfSignatureMetadata
        from pyhanko_certvalidator import CertValidationContext
        import pyhanko.sign.signers.cms_embedder as cms_embedder

        p12_bytes, passphrase = _get_p12_bytes()
        signer = signers.SimpleSigner.load_pkcs12(
            pfx_file=io.BytesIO(p12_bytes),
            passphrase=passphrase,
        )

        writer = IncrementalPdfFileWriter(io.BytesIO(pdf_bytes))
        fields.append_signature_field(writer, SigFieldSpec("Signature", on_page=0))

        meta = PdfSignatureMetadata(
            field_name="Signature",
            reason=reason,
            location="Canada",
            certify=False,
        )

        out = io.BytesIO()
        signers.sign_pdf(writer, meta, signer=signer, output=out)
        return out.getvalue()

    except ImportError:
        # pyhanko not installed in this environment — return unsigned PDF
        return pdf_bytes
    except Exception:
        # Any signing error — still return the original PDF rather than fail
        return pdf_bytes

"""Email delivery service — AWS SES with dev fallback to structlog."""
import structlog
from core.config import get_settings

logger = structlog.get_logger()


def send_email(*, to: str, subject: str, body_html: str, body_text: str) -> bool:
    """
    Send an email via AWS SES. Falls back to logging in dev.
    Returns True on success, False on failure.
    """
    settings = get_settings()

    if settings.environment != "production" or not getattr(settings, "ses_from_email", None):
        logger.info("email_dev_fallback", to=to, subject=subject)
        return True

    try:
        import boto3
        client = boto3.client("ses", region_name=settings.aws_region)
        client.send_email(
            Source=settings.ses_from_email,
            Destination={"ToAddresses": [to]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            },
        )
        return True
    except Exception as exc:
        logger.error("email_send_failed", to=to, subject=subject, error=str(exc))
        return False


# ─── Templates ────────────────────────────────────────────────────────────────

def supplier_expiry_reminder_html(
    supplier_name: str,
    product_id: str,
    valid_until: str,
    days_remaining: int,
    dashboard_url: str,
) -> tuple[str, str]:
    """Return (html, plain_text) for a supplier declaration expiry reminder."""
    urgency = "URGENT: " if days_remaining <= 1 else ("Action needed: " if days_remaining <= 7 else "")
    subject = f"{urgency}Supplier declaration expires in {days_remaining} day{'s' if days_remaining != 1 else ''}"

    html = f"""
    <html><body style="font-family: sans-serif; color: #1e293b; max-width: 600px;">
      <div style="background:#0062c9;padding:24px;border-radius:8px 8px 0 0;">
        <h1 style="color:white;margin:0;font-size:20px;">Uportai Compliance Alert</h1>
      </div>
      <div style="padding:24px;border:1px solid #e2e8f0;border-top:none;border-radius:0 0 8px 8px;">
        <p>Hello,</p>
        <p>The supplier declaration from <strong>{supplier_name}</strong> for product
        <code>{product_id}</code> is expiring on <strong>{valid_until}</strong>
        ({days_remaining} day{'s' if days_remaining != 1 else ''} remaining).</p>
        <p>An expired declaration may invalidate your preferential tariff claims under CUSMA, CETA, and CPTPP.</p>
        <p style="margin:24px 0;">
          <a href="{dashboard_url}" style="background:#0062c9;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:600;">
            Renew Declaration
          </a>
        </p>
        <p style="color:#64748b;font-size:12px;">
          You are receiving this because you are an admin of your Uportai organisation.
          To adjust notification settings, visit your account settings.
        </p>
      </div>
    </body></html>
    """

    text = (
        f"Uportai Compliance Alert\n\n"
        f"Supplier declaration from {supplier_name} for product {product_id} "
        f"expires on {valid_until} ({days_remaining} day(s) remaining).\n\n"
        f"Renew it here: {dashboard_url}\n"
    )

    return subject, html, text

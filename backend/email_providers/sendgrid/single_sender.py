"""
Single email sending via SendGrid
"""
import os
import time
from typing import Dict, Any
from loguru import logger
from .env_validator import _require_env

def send_one_sendgrid(
    to_email: str,
    subject: str,
    body_text: str,
    *,
    from_email: str,
    api_key: str | None = None,
    sandbox: bool = False,
    max_retries: int = 3,
    backoff_base: float = 1.0,
) -> int:
    """Send a single email via SendGrid using only to_email, subject, body (text/plain).

    Returns the HTTP status code (202 expected on success).
    """
    try:
        import sendgrid  # type: ignore
        from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization, MailSettings, SandBoxMode  # type: ignore
    except Exception:  # pragma: no cover
        raise RuntimeError("sendgrid package not installed. Add 'sendgrid' to requirements and install.")

    key = api_key or os.getenv("SENDGRID_API_KEY")
    if not key:
        raise ValueError("SENDGRID_API_KEY not set (env or parameter)")

    sg = sendgrid.SendGridAPIClient(api_key=key)
    mail = Mail()
    mail.from_email = Email(from_email)
    mail.subject = subject

    p = Personalization()
    p.add_to(To(to_email))
    mail.add_personalization(p)

    # Only text/plain per requirement
    mail.add_content(Content("text/plain", body_text or ""))

    if sandbox:
        mail.mail_settings = MailSettings()
        mail.mail_settings.sandbox_mode = SandBoxMode(enable=True)

    attempt = 0
    while True:
        attempt += 1
        resp = sg.client.mail.send.post(request_body=mail.get())
        if resp.status_code == 202:
            return resp.status_code
        if resp.status_code in (429, 500, 502, 503) and attempt < max_retries:
            sleep_s = backoff_base * (2 ** (attempt - 1))
            logger.warning(f"SendGrid {resp.status_code}; retrying in {sleep_s:.1f}s (attempt {attempt}/{max_retries})")
            time.sleep(sleep_s)
            continue
        return resp.status_code

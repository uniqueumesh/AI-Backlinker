"""
Single email sending via MailerSend
"""
import os
import time
from typing import Dict, Any
from loguru import logger
from .env_validator import _require_env

def send_one_mailersend(
    to_email: str,
    subject: str,
    body_text: str,
    *,
    from_email: str,
    api_key: str | None = None,
    max_retries: int = 3,
    backoff_base: float = 1.0,
) -> int:
    """Send a single email via MailerSend using only to_email, subject, body (text/plain).

    Returns the HTTP status code (202 expected on success).
    """
    try:
        from mailersend import emails as mailersend_emails  # type: ignore
    except Exception:  # pragma: no cover
        raise RuntimeError("mailersend package not installed. Add 'mailersend' to requirements and install.")

    key = api_key or os.getenv("MAILERSEND_API_KEY")
    if not key:
        raise ValueError("MAILERSEND_API_KEY not set (env or parameter)")

    mailer = mailersend_emails.MailerSend(api_key=key)

    mail_body = {
        "from": {
            "email": from_email,
            "name": "ALwrity Backlinker"
        },
        "to": [
            {
                "email": to_email,
                "name": "Recipient"
            }
        ],
        "subject": subject,
        "text": body_text or ""
    }

    attempt = 0
    while True:
        attempt += 1
        try:
            response = mailer.send(mail_body)
            if response.status_code == 202:
                return response.status_code
            if response.status_code in (429, 500, 502, 503) and attempt < max_retries:
                sleep_s = backoff_base * (2 ** (attempt - 1))
                logger.warning(f"MailerSend {response.status_code}; retrying in {sleep_s:.1f}s (attempt {attempt}/{max_retries})")
                time.sleep(sleep_s)
                continue
            return response.status_code
        except Exception as exc:
            if attempt < max_retries:
                sleep_s = backoff_base * (2 ** (attempt - 1))
                logger.warning(f"MailerSend exception; retrying in {sleep_s:.1f}s (attempt {attempt}/{max_retries}): {exc}")
                time.sleep(sleep_s)
                continue
            raise

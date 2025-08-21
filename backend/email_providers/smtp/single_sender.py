"""
Single email sending via SMTP
"""
import time
import smtplib
from email.mime.text import MIMEText
from loguru import logger
from .env_validator import _require_env

def send_one_smtp(
    to_email: str,
    subject: str,
    body_text: str,
    *,
    from_email: str,
    smtp_server: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    max_retries: int = 3,
    backoff_base: float = 1.0,
) -> bool:
    """Send a single email via SMTP.

    Returns True if the email was sent successfully, False otherwise.
    """
    try:
        msg = MIMEText(body_text, 'plain')
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        attempt = 0
        while True:
            attempt += 1
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                server.quit()
                logger.info(f"Email sent successfully to {to_email}")
                return True
            except Exception as exc:
                if attempt < max_retries:
                    sleep_s = backoff_base * (2 ** (attempt - 1))
                    logger.warning(f"SMTP attempt {attempt} failed; retrying in {sleep_s:.1f}s: {exc}")
                    time.sleep(sleep_s)
                    continue
                logger.error(f"Failed to send email to {to_email} after {max_retries} attempts: {exc}")
                return False
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

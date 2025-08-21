"""
Main dispatcher for email sending operations
"""
import os
from typing import List, Dict, Optional
from ..sendgrid import send_bulk_sendgrid
from ..mailersend import send_bulk_mailersend
from .bulk_sender import send_bulk_smtp

def send_bulk_emails(
    in_csv: str,
    *,
    provider: str = "smtp",
    from_email: str,
    smtp_server: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
    sendgrid_api_key: Optional[str] = None,
    mailersend_api_key: Optional[str] = None,
    rate_limit_per_sec: float = 10.0,
    dry_run: bool = False,
    sandbox: bool = False,
) -> List[Dict]:
    """Bulk send emails using the specified provider.

    Args:
        in_csv: Path to CSV file with columns: to_email, subject, body
        provider: One of "smtp", "sendgrid", or "mailersend"
        from_email: Sender email address
        smtp_*: SMTP configuration (will use environment variables if not provided)
        sendgrid_api_key: SendGrid API key (required if provider is "sendgrid")
        mailersend_api_key: MailerSend API key (required if provider is "mailersend")
        rate_limit_per_sec: Maximum emails per second
        dry_run: If True, don't actually send emails
        sandbox: If True, use sandbox mode (SendGrid only)

    Returns:
        List of outcomes per row
    """
    provider = provider.lower()
    
    if provider == "smtp":
        # Read SMTP credentials from environment if not provided
        smtp_server = smtp_server or os.getenv("SMTP_HOST")
        smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        smtp_user = smtp_user or os.getenv("SMTP_USER")
        smtp_password = smtp_password or os.getenv("SMTP_PASS")
        
        if not all([smtp_server, smtp_port, smtp_user, smtp_password]):
            raise ValueError("SMTP provider requires smtp_server, smtp_port, smtp_user, and smtp_password. Please set these in your .env file or provide them in the request.")
        
        return send_bulk_smtp(
            in_csv=in_csv,
            from_email=from_email,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            rate_limit_per_sec=rate_limit_per_sec,
            dry_run=dry_run,
        )
    elif provider == "sendgrid":
        if not sendgrid_api_key:
            raise ValueError("SendGrid provider requires sendgrid_api_key")
        return send_bulk_sendgrid(
            in_csv=in_csv,
            from_email=from_email,
            api_key=sendgrid_api_key,
            sandbox=sandbox,
            rate_limit_per_sec=rate_limit_per_sec,
            dry_run=dry_run,
        )
    elif provider == "mailersend":
        if not mailersend_api_key:
            raise ValueError("MailerSend provider requires mailersend_api_key")
        return send_bulk_mailersend(
            in_csv=in_csv,
            from_email=from_email,
            api_key=mailersend_api_key,
            rate_limit_per_sec=rate_limit_per_sec,
            dry_run=dry_run,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}. Must be one of: smtp, sendgrid, mailersend")

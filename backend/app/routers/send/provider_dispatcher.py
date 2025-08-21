"""
Provider dispatch logic for email sending
"""
from typing import List
from loguru import logger
from email_providers import send_bulk_sendgrid, send_bulk_mailersend
from email_providers.smtp import send_bulk_emails

def dispatch_to_provider(provider: str, input_csv: str, req_params: dict) -> List[dict]:
    """
    Dispatch email sending to the appropriate provider.
    
    Args:
        provider: Email provider name (sendgrid, mailersend, smtp)
        input_csv: Path to input CSV file
        req_params: Request parameters for the provider
        
    Returns:
        List[dict]: Results from the send operation
        
    Raises:
        ValueError: If provider is not supported
    """
    provider = provider.strip().lower()
    if provider == "sendgrid":
        results = send_bulk_sendgrid(
            input_csv,
            from_email=req_params["from_email"],
            api_key=req_params["sendgrid_key"],
            sandbox=bool(req_params.get("sandbox")),
            rate_limit_per_sec=req_params.get("rate_limit_per_sec"),
            dry_run=req_params.get("dry_run"),
        )
    elif provider == "mailersend":
        # SDK uses env MAILERSEND_API_KEY if api_key not set here
        if req_params.get("mailersend_key"):
            # Temporarily set env for this process if provided
            import os
            os.environ["MAILERSEND_API_KEY"] = req_params["mailersend_key"]
        results = send_bulk_mailersend(
            input_csv,
            from_email=req_params["from_email"],
            rate_limit_per_sec=req_params.get("rate_limit_per_sec"),
            dry_run=req_params.get("dry_run"),
        )
    elif provider == "smtp":
        results = send_bulk_emails(
            input_csv,
            from_email=req_params["from_email"],
            smtp_server=req_params["smtp_host"],
            smtp_port=req_params["smtp_port"],
            smtp_user=req_params["smtp_user"],
            smtp_password=req_params["smtp_pass"],
            rate_limit_per_sec=req_params.get("rate_limit_per_sec"),
            dry_run=req_params.get("dry_run"),
        )
    else:
        raise ValueError("provider must be one of: sendgrid, mailersend, smtp")
    
    return results

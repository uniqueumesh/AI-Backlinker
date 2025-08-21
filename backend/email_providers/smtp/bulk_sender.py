"""
Bulk email sending via SMTP
"""
import csv
import time
from typing import List, Dict
from loguru import logger
from .single_sender import send_one_smtp

def send_bulk_smtp(
    in_csv: str,
    *,
    from_email: str,
    smtp_server: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    rate_limit_per_sec: float = 10.0,
    dry_run: bool = False,
) -> List[Dict]:
    """Bulk send via SMTP from a CSV with columns: to_email, subject, body.

    Returns list of outcomes per row.
    """
    outcomes: List[Dict] = []
    delay = 1.0 / max(1.0, rate_limit_per_sec)

    # Count total emails for progress tracking
    with open(in_csv, "r", encoding="utf-8-sig") as f:
        total_emails = sum(1 for _ in csv.DictReader(f))
    
    logger.info(f"Starting to send {total_emails} emails via SMTP")

    with open(in_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            to_email = (row.get("to_email") or "").strip()
            subject = (row.get("subject") or "").strip()
            body = (row.get("body") or "").strip()

            if not to_email or not subject or not body:
                outcomes.append({
                    "row": i,
                    "to_email": to_email,
                    "status": "error",
                    "code": "missing_data",
                    "message": "Missing required field(s)"
                })
                continue

            if dry_run:
                outcomes.append({
                    "row": i,
                    "to_email": to_email,
                    "status": "dry_run",
                    "code": "200",
                    "message": "Would send email"
                })
                continue

            try:
                logger.info(f"Sending email {i}/{total_emails} to {to_email}")
                success = send_one_smtp(
                    to_email=to_email,
                    subject=subject,
                    body_text=body,
                    from_email=from_email,
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    smtp_user=smtp_user,
                    smtp_password=smtp_password,
                )
                if success:
                    outcomes.append({
                        "row": i,
                        "to_email": to_email,
                        "status": "sent",
                        "code": "200",
                        "message": "Email sent successfully"
                    })
                    logger.info(f"✅ Email {i}/{total_emails} sent successfully to {to_email}")
                else:
                    outcomes.append({
                        "row": i,
                        "to_email": to_email,
                        "status": "error",
                        "code": "smtp_failed",
                        "message": "SMTP send failed"
                    })
                    logger.error(f"❌ Email {i}/{total_emails} failed to send to {to_email}")
            except Exception as exc:
                outcomes.append({
                    "row": i,
                    "to_email": to_email,
                    "status": "error",
                    "code": "exception",
                    "message": str(exc)
                })
                logger.error(f"❌ Email {i}/{total_emails} exception for {to_email}: {exc}")

            if not dry_run:
                time.sleep(delay)

    logger.info(f"Completed sending {total_emails} emails. Success: {len([o for o in outcomes if o['status'] == 'sent'])}")
    return outcomes

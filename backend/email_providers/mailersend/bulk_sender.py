"""
Bulk email sending via MailerSend
"""
import csv
import time
from typing import List, Dict, Any
from loguru import logger
from .single_sender import send_one_mailersend

def send_bulk_mailersend(
    in_csv: str,
    *,
    from_email: str,
    api_key: str | None = None,
    rate_limit_per_sec: float = 10.0,
    dry_run: bool = False,
) -> List[Dict]:
    """Bulk send via MailerSend from a CSV with columns: to_email, subject, body.

    Returns list of outcomes per row.
    """
    outcomes: List[Dict] = []
    delay = 1.0 / max(1.0, rate_limit_per_sec)

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
                status_code = send_one_mailersend(
                    to_email=to_email,
                    subject=subject,
                    body_text=body,
                    from_email=from_email,
                    api_key=api_key,
                )
                if status_code == 202:
                    outcomes.append({
                        "row": i,
                        "to_email": to_email,
                        "status": "sent",
                        "code": str(status_code),
                        "message": "Email sent successfully"
                    })
                else:
                    outcomes.append({
                        "row": i,
                        "to_email": to_email,
                        "status": "error",
                        "code": str(status_code),
                        "message": f"MailerSend returned status {status_code}"
                    })
            except Exception as exc:
                outcomes.append({
                    "row": i,
                    "to_email": to_email,
                    "status": "error",
                    "code": "exception",
                    "message": str(exc)
                })

            if not dry_run:
                time.sleep(delay)

    return outcomes

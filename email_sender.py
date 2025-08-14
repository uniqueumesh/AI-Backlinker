import os
import csv
import time
import smtplib
from email.mime.text import MIMEText
from typing import Optional, Dict, List

from loguru import logger

try:
    import sendgrid  # type: ignore
    from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization, MailSettings, SandBoxMode  # type: ignore
except Exception:  # pragma: no cover
    sendgrid = None  # type: ignore


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def send_one_sendgrid(
    to_email: str,
    subject: str,
    body_text: str,
    *,
    from_email: str,
    api_key: Optional[str] = None,
    sandbox: bool = False,
    max_retries: int = 3,
    backoff_base: float = 1.0,
) -> int:
    """Send a single email via SendGrid using only to_email, subject, body (text/plain).

    Returns the HTTP status code (202 expected on success).
    """
    if sendgrid is None:
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


def send_bulk_sendgrid(
    in_csv: str,
    *,
    from_email: str,
    api_key: Optional[str] = None,
    sandbox: bool = False,
    rate_limit_per_sec: float = 10.0,
    dry_run: bool = False,
) -> List[Dict]:
    """Bulk send via SendGrid from a CSV with columns: to_email, subject, body.

    Returns list of outcomes per row.
    """
    outcomes: List[Dict] = []
    delay = 1.0 / max(1.0, rate_limit_per_sec)

    with open(in_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            to_email = (row.get("to_email") or "").strip()
            subject = row.get("subject") or ""
            body = row.get("body") or ""
            if not to_email:
                outcomes.append({"row": i, "to_email": "", "status": "skipped", "code": 0})
                continue

            if dry_run:
                logger.info(f"[dry-run] would send to {to_email}: {subject}")
                outcomes.append({"row": i, "to_email": to_email, "status": "dry_run"})
                continue

            code = send_one_sendgrid(
                to_email=to_email,
                subject=subject,
                body_text=body,
                from_email=from_email,
                api_key=api_key,
                sandbox=sandbox,
            )
            status = "sent" if code == 202 else "error"
            outcomes.append({"row": i, "to_email": to_email, "status": status, "code": code})
            time.sleep(delay)

    return outcomes


def send_one_smtp(
    to_email: str,
    subject: str,
    body_text: str,
    *,
    from_email: str,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_pass: Optional[str] = None,
    use_tls: bool = True,
) -> bool:
    """Send a single email via SMTP (e.g., GoDaddy workspace email).

    Defaults: host=smtpout.secureserver.net, port=587 (TLS).
    Returns True on success.
    """
    host = smtp_host or os.getenv("SMTP_HOST") or "smtpout.secureserver.net"
    port = int(smtp_port or os.getenv("SMTP_PORT") or 587)
    user = smtp_user or os.getenv("SMTP_USER")
    pwd = smtp_pass or os.getenv("SMTP_PASS")
    if not (user and pwd):
        raise ValueError("SMTP_USER/SMTP_PASS not set (env or parameters)")

    msg = MIMEText(body_text or "", _charset="utf-8")
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    with smtplib.SMTP(host, port, timeout=30) as server:
        if use_tls:
            server.starttls()
        server.login(user, pwd)
        server.sendmail(from_email, [to_email], msg.as_string())
    return True


def send_bulk_smtp(
    in_csv: str,
    *,
    from_email: str,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_pass: Optional[str] = None,
    rate_limit_per_sec: float = 10.0,
    dry_run: bool = False,
) -> List[Dict]:
    """Bulk send via SMTP from a CSV with columns: to_email, subject, body.

    Returns list of outcomes per row.
    """
    outcomes: List[Dict] = []
    delay = 1.0 / max(1.0, rate_limit_per_sec)

    with open(in_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            to_email = (row.get("to_email") or "").strip()
            subject = row.get("subject") or ""
            body = row.get("body") or ""
            if not to_email:
                outcomes.append({"row": i, "to_email": "", "status": "skipped"})
                continue

            if dry_run:
                logger.info(f"[dry-run] would send to {to_email}: {subject}")
                outcomes.append({"row": i, "to_email": to_email, "status": "dry_run"})
                continue

            try:
                ok = send_one_smtp(
                    to_email=to_email,
                    subject=subject,
                    body_text=body,
                    from_email=from_email,
                    smtp_host=smtp_host,
                    smtp_port=smtp_port,
                    smtp_user=smtp_user,
                    smtp_pass=smtp_pass,
                )
                outcomes.append({"row": i, "to_email": to_email, "status": "sent" if ok else "error"})
            except Exception as exc:
                logger.error(f"SMTP send failed for {to_email}: {exc}")
                outcomes.append({"row": i, "to_email": to_email, "status": "error", "message": str(exc)})
            time.sleep(delay)

    return outcomes


if __name__ == "__main__":  # pragma: no cover
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Send emails from CSV via SendGrid or SMTP (GoDaddy).")
    parser.add_argument("--in-csv", required=True, help="Input CSV with columns: to_email, subject, body")
    parser.add_argument("--from-email", required=True, help="Sender address (must be verified for SendGrid)")
    parser.add_argument("--provider", choices=["sendgrid", "smtp"], default="sendgrid")
    parser.add_argument("--rate", type=float, default=10.0, help="Max emails per second")
    parser.add_argument("--dry-run", action="store_true")

    # SendGrid options
    parser.add_argument("--sendgrid-key", default=os.getenv("SENDGRID_API_KEY"))
    parser.add_argument("--sandbox", action="store_true")

    # SMTP options (GoDaddy)
    parser.add_argument("--smtp-host", default=os.getenv("SMTP_HOST") or "smtpout.secureserver.net")
    parser.add_argument("--smtp-port", type=int, default=int(os.getenv("SMTP_PORT") or 587))
    parser.add_argument("--smtp-user", default=os.getenv("SMTP_USER"))
    parser.add_argument("--smtp-pass", default=os.getenv("SMTP_PASS"))

    args = parser.parse_args()

    in_path = Path(args.in_csv)
    if not in_path.exists():
        raise SystemExit(f"Input CSV not found: {in_path}")

    if args.provider == "sendgrid":
        if not args.sendgrid_key:
            raise SystemExit("Missing SENDGRID_API_KEY (use --sendgrid-key or set env var)")
        results = send_bulk_sendgrid(
            str(in_path),
            from_email=args.from_email,
            api_key=args.sendgrid_key,
            sandbox=args.sandbox,
            rate_limit_per_sec=args.rate,
            dry_run=args.dry_run,
        )
    else:
        if not (args.smtp_user and args.smtp_pass):
            raise SystemExit("Missing SMTP_USER/SMTP_PASS (use flags or env)")
        results = send_bulk_smtp(
            str(in_path),
            from_email=args.from_email,
            smtp_host=args.smtp_host,
            smtp_port=args.smtp_port,
            smtp_user=args.smtp_user,
            smtp_pass=args.smtp_pass,
            rate_limit_per_sec=args.rate,
            dry_run=args.dry_run,
        )

    out = in_path.with_name(in_path.stem + "_send_results.csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["row", "to_email", "status", "code", "message"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow({
                "row": r.get("row", ""),
                "to_email": r.get("to_email", ""),
                "status": r.get("status", ""),
                "code": r.get("code", ""),
                "message": r.get("message", ""),
            })
    logger.info(f"Wrote send outcomes -> {out.resolve()}")



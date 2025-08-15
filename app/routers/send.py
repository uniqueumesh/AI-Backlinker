from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List
from pathlib import Path
import csv
from loguru import logger

from app.models import (
    SendStartRequest,
    SendStartResponse,
    SendStatusResponse,
)
from app.jobs import job_store

# Import existing sender functions unchanged
from email_sender import (
    send_bulk_sendgrid,
    send_bulk_mailersend,
    send_bulk_smtp,
)


router = APIRouter(prefix="/send", tags=["send"]) 


def _write_rows_to_temp_csv(rows: List[dict], job_id: str) -> Path:
    Path("data").mkdir(parents=True, exist_ok=True)
    temp_path = Path("data") / f"send_input_{job_id}.csv"
    with temp_path.open("w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["to_email", "subject", "body"]
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_MINIMAL,
            dialect="excel",
        )
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "to_email": (r.get("to_email") or "").strip(),
                "subject": r.get("subject") or "",
                "body": (r.get("body") or "").replace("\r"," ").replace("\n"," "),
            })
    return temp_path


def _run_send(job_id: str, req: SendStartRequest) -> None:
    try:
        job_store.update(job_id, status="running", progress=0.05)

        # Prepare input CSV
        input_csv: Path
        if req.in_csv:
            input_csv = Path(req.in_csv)
            if not input_csv.exists():
                raise ValueError(f"in_csv not found: {req.in_csv}")
        elif req.rows:
            rows = [r.dict() if hasattr(r, "dict") else r for r in req.rows]
            input_csv = _write_rows_to_temp_csv(rows, job_id)
        else:
            raise ValueError("Provide either in_csv or rows for sending")

        # Determine outcomes path
        out_csv = req.out_csv
        if not out_csv:
            Path("data").mkdir(parents=True, exist_ok=True)
            out_csv = str(Path("data") / f"send_{job_id}.csv")

        # Dispatch to provider
        job_store.update(job_id, progress=0.2)
        provider = (req.provider or "").strip().lower()
        if provider == "sendgrid":
            results = send_bulk_sendgrid(
                str(input_csv),
                from_email=req.from_email,
                api_key=req.sendgrid_key,
                sandbox=bool(req.sandbox),
                rate_limit_per_sec=req.rate_limit_per_sec,
                dry_run=req.dry_run,
            )
        elif provider == "mailersend":
            # SDK uses env MAILERSEND_API_KEY if api_key not set here
            if req.mailersend_key:
                # Temporarily set env for this process if provided
                import os
                os.environ["MAILERSEND_API_KEY"] = req.mailersend_key
            results = send_bulk_mailersend(
                str(input_csv),
                from_email=req.from_email,
                rate_limit_per_sec=req.rate_limit_per_sec,
                dry_run=req.dry_run,
            )
        elif provider == "smtp":
            results = send_bulk_smtp(
                str(input_csv),
                from_email=req.from_email,
                smtp_host=req.smtp_host,
                smtp_port=req.smtp_port,
                smtp_user=req.smtp_user,
                smtp_pass=req.smtp_pass,
                rate_limit_per_sec=req.rate_limit_per_sec,
                dry_run=req.dry_run,
            )
        else:
            raise ValueError("provider must be one of: sendgrid, mailersend, smtp")

        # Save outcomes CSV
        saved_path: str | None = None
        try:
            out_file = Path(out_csv)
            if out_file.parent:
                out_file.parent.mkdir(parents=True, exist_ok=True)
            with out_file.open("w", newline="", encoding="utf-8-sig") as f:
                fieldnames = ["row", "to_email", "status", "code", "message"]
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    extrasaction="ignore",
                    quoting=csv.QUOTE_MINIMAL,
                    dialect="excel",
                )
                writer.writeheader()
                for r in results:
                    writer.writerow({
                        "row": r.get("row", ""),
                        "to_email": r.get("to_email", ""),
                        "status": r.get("status", ""),
                        "code": r.get("code", ""),
                        "message": r.get("message", ""),
                    })
            saved_path = str(out_file.resolve())
        except Exception as exc:
            logger.warning(f"auto-save send outcomes CSV failed: {exc}")

        job_store.update(job_id, status="done", progress=1.0, result=results, meta={"saved_csv_path": saved_path})
    except Exception as exc:
        logger.error(f"send job failed: {exc}")
        job_store.update(job_id, status="error", error=str(exc))


@router.post("/start", response_model=SendStartResponse, summary="Start send job")
def start_send(req: SendStartRequest, bg: BackgroundTasks) -> SendStartResponse:
    job = job_store.create()
    bg.add_task(_run_send, job.job_id, req)
    return SendStartResponse(job_id=job.job_id)


@router.get("/status/{job_id}", response_model=SendStatusResponse, summary="Get send job status")
def send_status(job_id: str) -> SendStatusResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    saved_csv_path = None
    if job.status == "done":
        saved_csv_path = (job.meta or {}).get("saved_csv_path")
    return SendStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        error=job.error,
        results=job.result if job.status == "done" else None,
        saved_csv_path=saved_csv_path,
    )



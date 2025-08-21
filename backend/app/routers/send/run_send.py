"""
Run send job - orchestrates email sending process
"""
from typing import List
from loguru import logger
from pathlib import Path
from app.models import SendStartRequest
from app.jobs import job_store
from .temp_csv import _write_rows_to_temp_csv
from .provider_dispatcher import dispatch_to_provider
from .outcomes_csv import save_send_outcomes

def _run_send(job_id: str, req: SendStartRequest) -> None:
    """
    Execute the send job in the background.
    
    Args:
        job_id: Unique identifier for the job
        req: Send request parameters
    """
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
        
        # Prepare request parameters for provider dispatch
        req_params = {
            "from_email": req.from_email,
            "sendgrid_key": req.sendgrid_key,
            "mailersend_key": req.mailersend_key,
            "smtp_host": req.smtp_host,
            "smtp_port": req.smtp_port,
            "smtp_user": req.smtp_user,
            "smtp_pass": req.smtp_pass,
            "sandbox": req.sandbox,
            "rate_limit_per_sec": req.rate_limit_per_sec,
            "dry_run": req.dry_run,
        }
        
        results = dispatch_to_provider(provider, str(input_csv), req_params)

        # Save outcomes CSV using the extracted function
        saved_path = save_send_outcomes(results, out_csv)

        job_store.update(job_id, status="done", progress=1.0, result=results, meta={"saved_csv_path": saved_path})
    except Exception as exc:
        logger.error(f"send job failed: {exc}")
        job_store.update(job_id, status="error", error=str(exc))

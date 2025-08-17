from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List
from pathlib import Path
import csv
from loguru import logger

from app.models import (
    EmailGenerateStartRequest,
    EmailGenerateStartResponse,
    EmailGenerateStatusResponse,
    EmailRow,
)
from app.jobs import job_store
from app.routers.research import ResearchResultRow  # reuse model type

# Import core generators unchanged
from ai_backlinking import generate_emails_for_rows  # type: ignore


router = APIRouter(prefix="/emails", tags=["emails"])


def _run_email_generation(job_id: str, req: EmailGenerateStartRequest) -> None:
    try:
        job_store.update(job_id, status="running", progress=0.05)

        # Build source rows
        rows: List[dict]
        if req.rows:
            rows = [r.dict() if hasattr(r, "dict") else r for r in req.rows]
        elif req.research_job_id:
            rjob = job_store.get(req.research_job_id)
            if not rjob or rjob.status != "done" or not rjob.result:
                raise ValueError("research_job_id not found or not done")
            src = [r.dict() if hasattr(r, "dict") else r for r in rjob.result]
            if req.selected_urls:
                urls_set = set(req.selected_urls)
                rows = [r for r in src if (r.get("url") in urls_set)]
            else:
                rows = src
        else:
            raise ValueError("Provide either rows or research_job_id")

        # Prefer rows with contact_email
        with_email = [r for r in rows if r.get("contact_email")] 
        others = [r for r in rows if not r.get("contact_email")]
        selected = (with_email + others)[: req.take]

        # Generate
        job_store.update(job_id, progress=0.2)
        emails = generate_emails_for_rows(
            selected,
            subject=req.subject,
            your_name=req.your_name,
            your_email=req.your_email,
            proposed_topic=req.topic,
            provider=req.provider,
            model=req.model,
            gemini_api_key=req.gemini_key,
            openai_api_key=req.openai_key,
        )
        rows_out = [EmailRow(**e) for e in emails]

        # Save CSV
        saved_path: str | None = None
        try:
            out_csv = req.out_csv
            if not out_csv:
                Path("data").mkdir(parents=True, exist_ok=True)
                out_csv = str(Path("data") / f"emails_{job_id}.csv")
            out_file = Path(out_csv)
            if out_file.parent:
                out_file.parent.mkdir(parents=True, exist_ok=True)
            with out_file.open("w", newline="", encoding="utf-8-sig") as f:
                fieldnames = [
                    "to_email","subject","body","url","domain","title","context_source","excerpt_chars","status","note","provider","model"
                ]
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    extrasaction="ignore",
                    quoting=csv.QUOTE_MINIMAL,
                    dialect="excel",
                )
                writer.writeheader()
                for e in emails:
                    rec = dict(e)
                    rec["body"] = (rec.get("body") or "").replace("\r"," ").replace("\n"," ")[:4000]
                    writer.writerow(rec)
            saved_path = str(out_file.resolve())
        except Exception as exc:
            logger.warning(f"auto-save emails CSV failed: {exc}")

        job_store.update(job_id, status="done", progress=1.0, result=rows_out, meta={"saved_csv_path": saved_path})
    except Exception as exc:
        logger.error(f"email generation job failed: {exc}")
        job_store.update(job_id, status="error", error=str(exc))


@router.post("/generate/start", response_model=EmailGenerateStartResponse, summary="Start email generation job")
def start_email_generation(req: EmailGenerateStartRequest, bg: BackgroundTasks) -> EmailGenerateStartResponse:
    job = job_store.create()
    bg.add_task(_run_email_generation, job.job_id, req)
    return EmailGenerateStartResponse(job_id=job.job_id)


@router.get("/generate/status/{job_id}", response_model=EmailGenerateStatusResponse, summary="Get email generation job status")
def email_generation_status(job_id: str) -> EmailGenerateStatusResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    saved_csv_path = None
    if job.status == "done":
        saved_csv_path = (job.meta or {}).get("saved_csv_path")
    return EmailGenerateStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        error=job.error,
        results=job.result if job.status == "done" else None,
        saved_csv_path=saved_csv_path,
    )



"""
Run email generation job - orchestrates email creation process
"""
from typing import List
from loguru import logger
from app.models import EmailGenerateStartRequest, EmailRow
from app.jobs import job_store
from app.models import ResearchResultRow
from .csv_handler import save_emails_csv
from emails import generate_emails_for_rows

def _run_email_generation(job_id: str, req: EmailGenerateStartRequest) -> None:
    """
    Execute the email generation job in the background.
    
    Args:
        job_id: Unique identifier for the job
        req: Email generation request parameters
    """
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
        # Generate emails for ALL selected URLs, not limited by take parameter
        selected = with_email + others

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
            gemini_api_key=None,  # Use environment variable
            openai_api_key=None,  # Use environment variable
        )
        rows_out = [EmailRow(**e) for e in emails]

        # Save CSV using the extracted function
        saved_path = save_emails_csv(emails, None, job_id)  # Use default path

        job_store.update(job_id, status="done", progress=1.0, result=rows_out, meta={"saved_csv_path": saved_path})
    except Exception as exc:
        logger.error(f"email generation job failed: {exc}")
        job_store.update(job_id, status="error", error=str(exc))

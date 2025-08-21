"""
Email generation status endpoint - provides job progress and results
"""
from fastapi import APIRouter, HTTPException
from app.models import EmailGenerateStatusResponse
from app.jobs import job_store

router = APIRouter(prefix="/emails", tags=["emails"])

@router.get("/generate/status/{job_id}", response_model=EmailGenerateStatusResponse, summary="Get email generation job status")
def email_generation_status(job_id: str) -> EmailGenerateStatusResponse:
    """
    Get the status and results of an email generation job.
    
    Args:
        job_id: Unique identifier for the job
        
    Returns:
        EmailGenerateStatusResponse: Job status and results
        
    Raises:
        HTTPException: If job not found
    """
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

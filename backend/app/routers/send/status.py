"""
Send status endpoint - provides job progress and results
"""
from fastapi import APIRouter, HTTPException
from app.models import SendStatusResponse
from app.jobs import job_store

router = APIRouter(prefix="/send", tags=["send"])

@router.get("/status/{job_id}", response_model=SendStatusResponse, summary="Get send job status")
def send_status(job_id: str) -> SendStatusResponse:
    """
    Get the status and results of a send job.
    
    Args:
        job_id: Unique identifier for the job
        
    Returns:
        SendStatusResponse: Job status and results
        
    Raises:
        HTTPException: If job not found
    """
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

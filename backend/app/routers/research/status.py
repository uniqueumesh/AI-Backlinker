"""
Research status endpoint - provides job progress and results
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
from app.models import ResearchJobStatusResponse
from app.jobs import job_store

router = APIRouter(prefix="/research", tags=["research"])

@router.get("/status/{job_id}", response_model=ResearchJobStatusResponse, summary="Get research job status")
def research_status(job_id: str) -> ResearchJobStatusResponse:
    """
    Get the status and results of a research job.
    
    Args:
        job_id: Unique identifier for the job
        
    Returns:
        ResearchJobStatusResponse: Job status and results
        
    Raises:
        HTTPException: If job not found
    """
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    # Compute saved CSV path if defaulting
    saved_csv_path = None
    if job.status == "done":
        saved_csv_path = (job.meta or {}).get("saved_csv_path")
        if not saved_csv_path:
            # Default save path convention
            default_path = Path("data") / f"research_{job_id}.csv"
            if default_path.exists():
                saved_csv_path = str(default_path.resolve())
    return ResearchJobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        error=job.error,
        results=job.result if job.status == "done" else None,
        saved_csv_path=saved_csv_path,
    )

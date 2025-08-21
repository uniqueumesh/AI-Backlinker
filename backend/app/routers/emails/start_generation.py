"""
Start email generation endpoint - creates and queues email generation jobs
"""
from fastapi import APIRouter, BackgroundTasks
from app.models import EmailGenerateStartRequest, EmailGenerateStartResponse
from app.jobs import job_store
from .run_generation import _run_email_generation

router = APIRouter(prefix="/emails", tags=["emails"])

@router.post("/generate/start", response_model=EmailGenerateStartResponse, summary="Start email generation job")
def start_email_generation(req: EmailGenerateStartRequest, bg: BackgroundTasks) -> EmailGenerateStartResponse:
    """
    Start a new email generation job.
    
    Args:
        req: Email generation request parameters
        bg: Background task manager
        
    Returns:
        EmailGenerateStartResponse: Job ID for tracking
    """
    job = job_store.create()
    bg.add_task(_run_email_generation, job.job_id, req)
    return EmailGenerateStartResponse(job_id=job.job_id)

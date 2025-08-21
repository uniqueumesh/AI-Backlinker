"""
Start send endpoint - creates and queues send jobs
"""
from fastapi import APIRouter, BackgroundTasks
from app.models import SendStartRequest, SendStartResponse
from app.jobs import job_store
from .run_send import _run_send

router = APIRouter(prefix="/send", tags=["send"])

@router.post("/start", response_model=SendStartResponse, summary="Start send job")
def start_send(req: SendStartRequest, bg: BackgroundTasks) -> SendStartResponse:
    """
    Start a new send job.
    
    Args:
        req: Send request parameters
        bg: Background task manager
        
    Returns:
        SendStartResponse: Job ID for tracking
    """
    job = job_store.create()
    bg.add_task(_run_send, job.job_id, req)
    return SendStartResponse(job_id=job.job_id)

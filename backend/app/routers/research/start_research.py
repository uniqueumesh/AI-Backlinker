"""
Start research endpoint - creates and queues research jobs
"""
from fastapi import APIRouter, BackgroundTasks
from app.models import ResearchStartRequest, ResearchStartResponse
from app.jobs import job_store
from .run_research import _run_research

router = APIRouter(prefix="/research", tags=["research"])

@router.post("/start", response_model=ResearchStartResponse, summary="Start research job")
def start_research(req: ResearchStartRequest, bg: BackgroundTasks) -> ResearchStartResponse:
    """
    Start a new research job.
    
    Args:
        req: Research request parameters
        bg: Background task manager
        
    Returns:
        ResearchStartResponse: Job ID for tracking
    """
    job = job_store.create()
    bg.add_task(_run_research, job.job_id, req)
    return ResearchStartResponse(job_id=job.job_id)

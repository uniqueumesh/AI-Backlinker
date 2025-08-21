"""
Run research job - orchestrates the research process
"""
from typing import List
from loguru import logger
from app.models import ResearchStartRequest, ResearchResultRow
from app.jobs import job_store
from .build_row import _build_row_from_url
from .csv_handler import save_research_csv
from scraping import find_backlink_opportunities

def _run_research(job_id: str, req: ResearchStartRequest) -> None:
    """
    Execute the research job in the background.
    
    Args:
        job_id: Unique identifier for the job
        req: Research request parameters
    """
    try:
        job_store.update(job_id, status="running", progress=0.05)
        results: List[dict]
        if req.urls:
            results = [_build_row_from_url(u, req.firecrawl_key) for u in req.urls]
        else:
            if not req.keyword:
                raise ValueError("keyword is required when urls are not provided")
            results = find_backlink_opportunities(
                req.keyword,
                serper_api_key=req.serper_key,
                firecrawl_api_key=req.firecrawl_key,
                max_results=req.max_results,
            )
        rows = [ResearchResultRow(**r) for r in results]
        
        # Save CSV using the extracted function
        saved_path = save_research_csv(rows, req.out_csv, job_id)
        
        job_store.update(job_id, status="done", progress=1.0, result=rows if rows else [], meta={"saved_csv_path": saved_path})
    except Exception as exc:
        logger.error(f"research job failed: {exc}")
        job_store.update(job_id, status="error", error=str(exc))

"""
Run research job - orchestrates the research process
"""
from typing import List
from loguru import logger
from app.models import ResearchStartRequest, ResearchResultRow
from app.jobs import job_store
from .build_row import _build_row_from_url
from .csv_handler import save_research_results_to_csv
from scraping import find_backlink_opportunities
import os

async def _run_research(job_id: str, req: ResearchStartRequest) -> None:
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
            
            # Run Serper research
            job_store.update(job_id, status="running", progress=0.3, meta={"phase": "serper"})
            results = find_backlink_opportunities(
                req.keyword,
                serper_api_key=req.serper_key,
                firecrawl_api_key=req.firecrawl_key,
                max_results=req.max_results,
            )
        
        # Convert to ResearchResultRow objects
        logger.info(f"Converting {len(results)} results to ResearchResultRow objects")
        rows = [ResearchResultRow(**r) for r in results]
        

        
        # Save CSV using the extracted function
        if req.out_csv:
            # If specific output path provided, use it
            output_dir = os.path.dirname(req.out_csv) or "data"
            filename = os.path.basename(req.out_csv)
        else:
            # Default to data directory with job_id
            output_dir = "data"
            filename = f"research_{job_id}.csv"
        
        saved_path = save_research_results_to_csv(rows, output_dir, filename)
        
        job_store.update(job_id, status="done", progress=1.0, result=rows if rows else [], meta={"saved_csv_path": saved_path})
    except Exception as exc:
        logger.error(f"research job failed: {exc}")
        job_store.update(job_id, status="error", error=str(exc))

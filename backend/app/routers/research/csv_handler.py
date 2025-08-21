"""
CSV handling utilities for research results
"""
from pathlib import Path
import csv
from loguru import logger
from typing import List
from app.models import ResearchResultRow

def save_research_csv(rows: List[ResearchResultRow], out_csv: str | None, job_id: str) -> str | None:
    """
    Save research results to CSV file.
    
    Args:
        rows: List of research result rows
        out_csv: Optional output CSV path
        job_id: Job ID for default naming
        
    Returns:
        str | None: Path to saved CSV file, or None if failed
    """
    saved_path: str | None = None
    try:
        # Determine output path: request param or default data/research_{job_id}.csv
        if not out_csv:
            Path("data").mkdir(parents=True, exist_ok=True)
            out_csv = str(Path("data") / f"research_{job_id}.csv")
        out_file = Path(out_csv)
        if out_file.parent:
            out_file.parent.mkdir(parents=True, exist_ok=True)
        # Write with UTF-8 BOM so Excel shows content reliably
        with out_file.open("w", newline="", encoding="utf-8-sig") as f:
            fieldnames = [
                "url",
                "domain",
                "title",
                "contact_email",
                "contact_emails_all",
                "contact_form_url",
                "guidelines_url",
                "context_source",
                "page_excerpt",
            ]
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
                extrasaction="ignore",
                quoting=csv.QUOTE_MINIMAL,
                dialect="excel",
            )
            writer.writeheader()
            for r in rows:
                rec = r.dict()
                # Normalize values to strings and limit excerpt length
                page_excerpt = (rec.get("page_excerpt") or "").replace("\r", " ").replace("\n", " ")[:1000]
                row_out = {
                    "url": str(rec.get("url", "")),
                    "domain": str(rec.get("domain", "")),
                    "title": str(rec.get("title", "")),
                    "contact_email": str(rec.get("contact_email", "")),
                    "contact_emails_all": str(rec.get("contact_emails_all", "")),
                    "contact_form_url": str(rec.get("contact_form_url", "")),
                    "guidelines_url": str(rec.get("guidelines_url", "")),
                    "context_source": str(rec.get("context_source", "")),
                    "page_excerpt": page_excerpt,
                }
                writer.writerow(row_out)
            f.flush()
        saved_path = str(out_file.resolve())
    except Exception as exc:
        logger.warning(f"auto-save research CSV failed: {exc}")
    
    return saved_path

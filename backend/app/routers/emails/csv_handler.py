"""
CSV handling utilities for email generation results
"""
from pathlib import Path
import csv
from loguru import logger
from typing import List

def save_emails_csv(emails: List[dict], out_csv: str | None, job_id: str) -> str | None:
    """
    Save email generation results to CSV file.
    
    Args:
        emails: List of generated email data
        out_csv: Optional output CSV path
        job_id: Job ID for default naming
        
    Returns:
        str | None: Path to saved CSV file, or None if failed
    """
    saved_path: str | None = None
    try:
        out_csv = out_csv
        if not out_csv:
            Path("data").mkdir(parents=True, exist_ok=True)
            out_csv = str(Path("data") / f"emails_{job_id}.csv")
        out_file = Path(out_csv)
        if out_file.parent:
            out_file.parent.mkdir(parents=True, exist_ok=True)
        with out_file.open("w", newline="", encoding="utf-8-sig") as f:
            fieldnames = [
                "to_email","subject","body","url","domain","title","context_source","excerpt_chars","status","note","provider","model"
            ]
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
                extrasaction="ignore",
                quoting=csv.QUOTE_MINIMAL,
                dialect="excel",
            )
            writer.writeheader()
            for e in emails:
                rec = dict(e)
                rec["body"] = (rec.get("body") or "").replace("\r"," ").replace("\n"," ")[:4000]
                writer.writerow(rec)
        saved_path = str(out_file.resolve())
    except Exception as exc:
        logger.warning(f"auto-save emails CSV failed: {exc}")
    
    return saved_path
